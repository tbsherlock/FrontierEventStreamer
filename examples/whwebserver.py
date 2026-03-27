import asyncio
import logging
import os
import src.events as events
from src.scanner import ScannerConfig, WorldScanner, get_modules


WH_HOST = os.getenv("WH_HOST", "0.0.0.0")  # webhook host addr
WH_PORT = int(os.getenv("WH_HOST", 8765))  # webhook port
STATIC_HOST = os.getenv("STATIC_HOST", "0.0.0.0")  # static web server host addr
STATIC_PORT = int(os.getenv("STATIC_PORT", "8766"))  # static web server port
RPC_URL = os.getenv("RPC_URL", "https://fullnode.testnet.sui.io:443")  # testnet
#PACKAGE_ID = os.getenv("PACKAGE_ID", "0x28b497559d65ab320d9da4613bf2498d5946b2c0ae3597ccfda3072ce127448c")  # stillness
PACKAGE_ID = os.getenv("PACKAGE_ID", "0xd12a70c74c1e759445d6f209b01d43d860e97fcf2ef72ccbbd00afd828043f75")  # utopia


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
# Static data server
# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
import asyncio
import logging
import os
from aiohttp import web

STATIC_FILE = os.getenv("STATIC_FILE", "static/index.html")  # file to serve
logger = logging.getLogger(__name__)

async def _handle(request: web.Request) -> web.Response:
    return web.FileResponse(STATIC_FILE)

class StaticServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8766):
        self.host = host
        self.port = port
        self._app = web.Application()
        self._runner: web.AppRunner | None = None
        self._setup_routes()

    def _setup_routes(self) -> None:
        self._app.router.add_get("/", _handle)

    async def run(self) -> None:
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        site = web.TCPSite(self._runner, self.host, self.port)
        await site.start()
        logger.info(f"Static server serving '{STATIC_FILE}' on http://{self.host}:{self.port}")
        # Keep running until cancelled
        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            pass
        finally:
            await self.close()

    async def close(self) -> None:
        if self._runner:
            await self._runner.cleanup()
            logger.info("Static server shut down cleanly.")


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
# WebhookServer
# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----

import asyncio
import json
import logging
from aiohttp import web
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

@dataclass
class WHEvent:
    """A single event to be routed through the server."""
    channel: str          # routing key, e.g. "alerts", "metrics", "logs"
    type: str             # event type label, e.g. "info", "warning", "error"
    description: str      # human-readable description
    time: Optional[str] = None   # ISO-8601; auto-filled if omitted

    def __post_init__(self):
        if self.time is None:
            self.time = datetime.now(timezone.utc).isoformat()


class ChannelBroker:
    """
    Maintains a registry of SSE response queues keyed by channel name.
    One client may subscribe to many channels; one channel may have many clients.
    """

    def __init__(self):
        # channel -> set of asyncio.Queue (one per subscribed client)
        self._subscribers: dict[str, set[asyncio.Queue]] = {}

    def subscribe(self, channels: list[str]) -> tuple[asyncio.Queue, list[str]]:
        """Register a client queue for the given channels.  Returns (queue, channels)."""
        q: asyncio.Queue = asyncio.Queue()
        for ch in channels:
            self._subscribers.setdefault(ch, set()).add(q)
        log.info("Client subscribed to channels: %s", channels)
        return q, channels

    def unsubscribe(self, q: asyncio.Queue, channels: list[str]):
        """Remove a client queue from all its channels."""
        for ch in channels:
            self._subscribers.get(ch, set()).discard(q)
        log.info("Client unsubscribed from channels: %s", channels)

    async def publish(self, event: WHEvent):
        """Fan-out an event to every queue subscribed to event.channel."""
        targets = self._subscribers.get(event.channel, set())
        if not targets:
            log.debug("No subscribers for channel '%s'", event.channel)
            return
        payload = json.dumps(asdict(event))
        for q in list(targets):
            await q.put(payload)
        log.debug("Published to %d client(s) on channel '%s'", len(targets), event.channel)


class WebhookServer:
    """
    Reads Event objects from *queue* and broadcasts them to SSE subscribers.

    Parameters
    ----------
    queue   : asyncio.Queue populated by your application code
    host    : bind address  (default "0.0.0.0")
    port    : TCP port      (default 8765)
    """

    def __init__(self, queue: asyncio.Queue, host: str = "0.0.0.0", port: int = 8765):
        self._queue = queue
        self._host = host
        self._port = port
        self._broker = ChannelBroker()

    # ------------------------------------------------------------------
    # HTTP handlers
    # ------------------------------------------------------------------

    async def _handle_subscribe(self, request: web.Request) -> web.StreamResponse:
        """
        GET /subscribe?channels=ch1,ch2
        Streams SSE events to the client for as long as the connection is open.
        """
        raw = request.rel_url.query.get("channels", "")
        channels = [c.strip() for c in raw.split(",") if c.strip()]
        if not channels:
            raise web.HTTPBadRequest(reason="?channels= query param required (comma-separated)")

        response = web.StreamResponse(headers={
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",          # disable nginx buffering if present
            "Access-Control-Allow-Origin": "*",  # allow browser clients
        })
        await response.prepare(request)

        client_q, subscribed = self._broker.subscribe(channels)
        try:
            # Send a comment to confirm connection
            await response.write(b": connected\n\n")
            while True:
                payload = await client_q.get()
                await response.write(f"data: {payload}\n\n".encode())
        except (ConnectionResetError, asyncio.CancelledError):
            pass
        finally:
            self._broker.unsubscribe(client_q, subscribed)

        return response

    async def _handle_health(self, _request: web.Request) -> web.Response:
        return web.Response(text="ok")

    # ------------------------------------------------------------------
    # Background task: drain the application queue
    # ------------------------------------------------------------------

    async def _dispatch_loop(self):
        """Continuously read events from the application queue and publish them."""
        log.info("Dispatch loop started")
        while True:
            event = await self._queue.get()
            if not isinstance(event, WHEvent):
                log.warning("Dropping non-Event object: %r", event)
                continue
            #log.info("Dispatching event: channel=%s type=%s", event.channel, event.type)
            await self._broker.publish(event)

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    async def run(self):
        app = web.Application()
        app.router.add_get("/subscribe", self._handle_subscribe)
        app.router.add_get("/health", self._handle_health)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self._host, self._port)
        await site.start()
        log.info("Webhook server listening on http://%s:%d", self._host, self._port)

        await self._dispatch_loop()   # runs forever



# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
# Entry
# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
event_queue = asyncio.Queue()


def event_callback(event: events.EventBase) -> None:
    formatted_datetime = event.emitted_at.strftime("%Y-%m-%d %H:%M:%S")
    event_queue.put_nowait(WHEvent(channel=event.module, type=event.event_type, description=event.to_str(), time=formatted_datetime))


async def main():
    config = ScannerConfig(
        rpc_url = RPC_URL,
        package_id = PACKAGE_ID,
        checkpoint_poll_interval = 1.0,
        event_page_size          = 50,
    )

    whserver = WebhookServer(event_queue, host=WH_HOST, port=WH_PORT)
    staticserver = StaticServer(host=STATIC_HOST, port=STATIC_PORT)

    scanner = WorldScanner(config)

    modules = get_modules()
    scanner.register_cb(None, event_callback)
    print(f"Scanning world package: {config.package_id}")
    print(f"Watching {len(modules)} modules: {', '.join(modules)}")
    print("─" * 60)

    try:
        # Run the main ongoing tasks
        results = await asyncio.gather(
            *[scanner.start(), whserver.run(), staticserver.run()],
            return_exceptions=True,
        )

        #await scanner.start()
        #await whserver.run()
    except KeyboardInterrupt:
        pass
    finally:
        await scanner.close()
        print("Scanner shut down cleanly.")


if __name__ == "__main__":
    asyncio.run(main())



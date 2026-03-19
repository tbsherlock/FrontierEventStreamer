"""
EVE Frontier Event Scanner
============================================
Monitors all event types emitted by the `world` package.

Polling is checkpoint-driven (one Sui checkpoint ≈ one block).
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

import httpx

from src.events import EVENT_REGISTRY, NetworkNodeCreatedEvent


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("world_scanner")
logging.getLogger("httpx").setLevel(logging.WARNING)


# ---------------------------------------------------------------------------
# Derive the unique module list from EVENT_REGISTRY
# ---------------------------------------------------------------------------

def get_modules() -> list[str]:
    """Return the ordered, deduplicated list of module names from EVENT_REGISTRY."""
    seen: set[str] = set()
    modules: list[str] = []
    for mod, _struct in EVENT_REGISTRY:
        if mod not in seen:
            seen.add(mod)
            modules.append(mod)
    return modules


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

@dataclass
class ScannerConfig:
    rpc_url: str  # Which RPC endpoint to use
    package_id: str  # The on chain address

    # How often to check for a new checkpoint (seconds).
    checkpoint_poll_interval: float = 1.0
    event_page_size: int  = 50
    max_retries:     int  = 5
    retry_backoff:   float = 2.0


# ---------------------------------------------------------------------------
# Low-level JSON-RPC client
# ---------------------------------------------------------------------------

class SuiRpcClient:
    def __init__(self, config: ScannerConfig):
        self.config  = config
        self._http   = httpx.AsyncClient(timeout=30)
        self._req_id = 0

    async def call(self, method: str, params: list) -> Any:
        self._req_id += 1
        payload = {"jsonrpc": "2.0", "id": self._req_id, "method": method, "params": params}
        for attempt in range(self.config.max_retries):
            try:
                resp = await self._http.post(
                    self.config.rpc_url, json=payload,
                    headers={"Content-Type": "application/json"},
                )
                resp.raise_for_status()
                data = resp.json()
                if "error" in data:
                    raise RuntimeError(f"RPC error: {data['error']}")
                return data.get("result")
            except (httpx.HTTPError, RuntimeError) as exc:
                wait = self.config.retry_backoff * (2 ** attempt)
                logger.warning(f"RPC '{method}' attempt {attempt+1} failed: {exc}. Retry in {wait:.1f}s…")
                await asyncio.sleep(wait)
        raise RuntimeError(f"RPC call '{method}' failed after {self.config.max_retries} retries")

    async def close(self):
        await self._http.aclose()


# ---------------------------------------------------------------------------
# Per-module stream state
# ---------------------------------------------------------------------------

@dataclass
class FilterStream:
    """Tracks cursor state for one Move module filter."""
    module:      str
    filter_dict: dict          # {"MoveModule": {"package": "...", "module": "..."}}
    cursor:      Optional[dict] = None


# ---------------------------------------------------------------------------
# World Scanner
# ---------------------------------------------------------------------------

class WorldScanner:
    """
    Polls the Sui chain for new checkpoints and, on each advance, drains all
    new events across every world contract module.
    """

    def __init__(self, config: ScannerConfig):
        self.config = config
        self.rpc    = SuiRpcClient(self.config)

        # One FilterStream per unique module derived from EVENT_REGISTRY
        self._streams: list[FilterStream] = [
            FilterStream(
                module      = mod,
                filter_dict = {
                    "MoveModule": {
                        "package": self.config.package_id,
                        "module":  mod,
                    }
                },
            )
            for mod in get_modules()
        ]

        self._last_checkpoint: Optional[int] = None
        self._running = False
        self._callback_fn = None

    # ------------------------------------------------------------------ run

    async def start(self):
        self._running = True
        logger.info(
            f"WorldScanner starting | RPC={self.config.rpc_url} | "
            f"package={self.config.package_id} | "
            f"watching {len(self._streams)} modules"
        )

        # Bootstrap all cursors to the current chain tip
        self._last_checkpoint = await self._latest_checkpoint()
        await asyncio.gather(*[self._bootstrap_stream(s) for s in self._streams])
        logger.info(f"Bootstrapped at checkpoint {self._last_checkpoint}")

        while self._running:
            t0 = time.monotonic()
            try:
                await self._tick()
            except Exception as exc:
                logger.error(f"Tick error: {exc}", exc_info=True)
            sleep_for = max(0.0, self.config.checkpoint_poll_interval - (time.monotonic() - t0))
            await asyncio.sleep(sleep_for)

    def stop(self):
        self._running = False

    async def close(self):
        self.stop()
        await self.rpc.close()

    def register_cb(self, event_type, callback_fn: Callable) -> None:
        """ Register a callback function, to be called on event occurrence """
        self._callback_fn = callback_fn

    # ------------------------------------------------------------------ tick

    async def _tick(self):
        latest = await self._latest_checkpoint()
        if latest == self._last_checkpoint:
            return

        logger.debug(f"Checkpoint {self._last_checkpoint} → {latest} (+{latest - self._last_checkpoint})")

        # Drain all streams concurrently
        results = await asyncio.gather(
            *[self._drain_stream(s) for s in self._streams],
            return_exceptions=True,
        )

        total = 0
        for i, res in enumerate(results):
            if isinstance(res, Exception):
                logger.error(f"Error draining stream '{self._streams[i].module}': {res}")
            else:
                total += res

        if total:
            logger.info(f"Checkpoint {latest}: {total} new event(s) across all modules")

        self._last_checkpoint = latest

    # ------------------------------------------------------------------ stream helpers

    async def _bootstrap_stream(self, stream: FilterStream):
        """Set cursor to the current tip so we only emit future events."""
        try:
            result = await self.rpc.call(
                "suix_queryEvents",
                [stream.filter_dict, None, 1, True],
            )
            stream.cursor = result.get("nextCursor")

        except Exception as exc:
            logger.warning(f"Could not bootstrap stream '{stream.module}': {exc}")

    async def _drain_stream(self, stream: FilterStream) -> int:
        """Fetch all new events for this module stream, parse and print them. Returns count."""
        collected = 0
        cursor = stream.cursor

        while True:
            result = await self.rpc.call(
                "suix_queryEvents",
                [stream.filter_dict, cursor, self.config.event_page_size, False],  # ascending
            )

            page = result.get("data", [])
            for raw in page:
                self._on_event(stream, raw)
                collected += 1

            if result.get("hasNextPage") and result.get("nextCursor"):
                cursor = result["nextCursor"]
            else:
                if result.get("nextCursor"):
                    stream.cursor = result["nextCursor"]
                break

        return collected

    # ------------------------------------------------------------------ printing

    def _on_event(self, stream: FilterStream, raw: dict):
        # Derive the struct name from the event's type field, e.g.
        # "0xabc::killmail::KillmailCreatedEvent" → "KillmailCreatedEvent"
        event_type_str: str = raw.get("type", "")
        struct_name = event_type_str.rsplit("::", 1)[-1] if "::" in event_type_str else ""

        key = (stream.module, struct_name)
        parser = EVENT_REGISTRY.get(key)

        if parser:
            try:
                evt = parser(raw)
                self._callback_fn(evt)
                return
            except Exception as exc:
                logger.error(f"Parse error for {stream.module}::{struct_name}: {exc}")
        else:
            logger.warning(f"No parser for {key}")

    # ------------------------------------------------------------------ helpers

    async def _latest_checkpoint(self) -> int:
        return int(await self.rpc.call("sui_getLatestCheckpointSequenceNumber", []))



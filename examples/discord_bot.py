"""
Discord bot that reads Event objects from an async queue and posts
their string descriptions to a specified channel.
"""

import asyncio
import logging
import os
import discord

from src import events
from src.events import EventBase
from src.scanner import WorldScanner, ScannerConfig, get_modules

logger = logging.getLogger(__name__)



# ---------------------------------------------------------------------------
# Bot
# ---------------------------------------------------------------------------

class EventForwarderBot(discord.Client):
    """
    A Discord client that drains an asyncio.Queue[Event] and forwards
    each event's description to a Discord channel.

    Parameters
    ----------
    queue:
        The shared async queue that produces Event objects.
    channel_id:
        The numeric ID of the Discord channel to post messages to.
    **kwargs:
        Forwarded to discord.Client (e.g. intents=...).
    """

    def __init__(
        self,
        queue: asyncio.Queue,
        channel_id: int,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._queue = queue
        self._channel_id = channel_id
        self._forwarder_task: asyncio.Task | None = None

    # ------------------------------------------------------------------
    # discord.Client lifecycle hooks
    # ------------------------------------------------------------------

    async def on_ready(self) -> None:
        logger.info("Logged in as %s (id=%s)", self.user, self.user.id)
        # Start the queue-draining loop once the bot is connected.
        self._forwarder_task = asyncio.create_task(
            self._forward_events(), name="event-forwarder"
        )

    async def close(self) -> None:
        """Gracefully cancel the forwarder task before disconnecting."""
        if self._forwarder_task and not self._forwarder_task.done():
            self._forwarder_task.cancel()
            try:
                await self._forwarder_task
            except asyncio.CancelledError:
                pass
        await super().close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _forward_events(self) -> None:
        """
        Continuously waits for events on the queue and posts them to
        the Discord channel. Runs until cancelled.
        """
        channel = await self._resolve_channel()
        if channel is None:
            logger.error(
                "Channel %s not found or not a text channel. Forwarder stopping.",
                self._channel_id,
            )
            return

        logger.info("Forwarding events to #%s (%s)", channel.name, channel.id)

        while True:
            try:
                event: EventBase = await self._queue.get()
            except asyncio.CancelledError:
                logger.info("Event forwarder cancelled.")
                raise

            try:
                message = event.to_str()
                await channel.send(message)
                logger.debug("Sent event: %s", message)
            except discord.DiscordException as exc:
                logger.error("Failed to send event to Discord: %s", exc)
            finally:
                self._queue.task_done()

    async def _resolve_channel(self) -> discord.TextChannel | None:
        """Fetch and validate the target channel."""
        channel = self.get_channel(self._channel_id)
        if channel is None:
            # Not in cache yet — try a direct fetch.
            try:
                channel = await self.fetch_channel(self._channel_id)
            except discord.NotFound:
                return None

        if not isinstance(channel, discord.TextChannel):
            logger.error("Channel %s is not a TextChannel.", self._channel_id)
            return None

        return channel


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
# Entry
# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
event_queue = asyncio.Queue()
intents = discord.Intents.default()


def event_callback(event: events.EventBase) -> None:
    event_queue.put_nowait(event)


async def main():
    TOKEN = os.environ["DISCORD_BOT_TOKEN"]
    CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])
    RPC_URL = os.getenv("RPC_URL", "https://fullnode.testnet.sui.io:443")  # testnet
    PACKAGE_ID = os.getenv("PACKAGE_ID", "0xd12a70c74c1e759445d6f209b01d43d860e97fcf2ef72ccbbd00afd828043f75")  # utopia


    config = ScannerConfig(
        rpc_url = RPC_URL,
        package_id = PACKAGE_ID,
        checkpoint_poll_interval = 1.0,
        event_page_size          = 50,
    )

    scanner = WorldScanner(config)

    modules = get_modules()
    scanner.register_cb(None, event_callback)
    print(f"Scanning world package: {config.package_id}")
    print(f"Watching {len(modules)} modules: {', '.join(modules)}")
    print("─" * 60)

    bot = EventForwarderBot(queue=event_queue, channel_id=CHANNEL_ID, intents=intents)

    try:
        # Run the main ongoing tasks
        results = await asyncio.gather(
            *[scanner.start(), bot.start(TOKEN)],
            return_exceptions=True,
        )

    except KeyboardInterrupt:
        pass
    finally:
        await scanner.close()
        print("Scanner shut down cleanly.")


if __name__ == "__main__":
    asyncio.run(main())
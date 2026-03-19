# Example usage, initialise the scanner and print events to stdout
import asyncio
import os
from src.scanner import ScannerConfig, WorldScanner, get_modules

RPC_URL = os.getenv("RPC_URL", "https://fullnode.testnet.sui.io:443")  # testnet
PACKAGE_ID = os.getenv("PACKAGE_ID", "0x28b497559d65ab320d9da4613bf2498d5946b2c0ae3597ccfda3072ce127448c")  # stillness
#PACKAGE_ID = os.getenv("PACKAGE_ID", "0xd12a70c74c1e759445d6f209b01d43d860e97fcf2ef72ccbbd00afd828043f75")  # utopia


def event_callback(event) -> None:
    print(f"event_callback: {event}")

async def main():
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

    try:
        await scanner.start()
    except KeyboardInterrupt:
        pass
    finally:
        await scanner.close()
        print("Scanner shut down cleanly.")


if __name__ == "__main__":
    asyncio.run(main())

import sys
import asyncio

from src.ytb_dl_service.consumer.client import main as client
from src.ytb_dl_service.producer.server import main as server


async def main():
    arg = sys.argv.pop()
    if arg == "client":
        return await client()
    if arg == "server":
        return await server()
    raise Exception(f"Arg {arg} not expected!")


if __name__ == "__main__":
    asyncio.run(main())

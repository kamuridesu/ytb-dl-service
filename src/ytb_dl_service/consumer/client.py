import asyncio
import json
import os

import aiohttp
from Shimarin.client.events import Event, EventPolling, EventsHandlers
from yt_dlp import YoutubeDL

handlers = EventsHandlers()


def longer_than_10_minutes(info, *, _):
    duration = info.get('duration')
    if duration and duration < 600:
        return 'The video is too short'


ytdl_opts = {
    "match_filter": longer_than_10_minutes,
    "format": "best[height<=480]",
    "outtmpl": "%(title)s.%(ext)s"
}


@handlers.new("new_url")
async def new_url(event: Event):
    async with aiohttp.ClientSession() as s:
        event.__session = s
        if event.payload is None:
            return await event.reply(json.dumps({"msg": "Invalid URL"}), metadata={"error": "1"})
        url = event.payload
        try:
            with YoutubeDL(ytdl_opts) as ytdl:
                info = ytdl.extract_info(url, download=True)
                filepath = ytdl.prepare_filename(info)
                with open(filepath, "rb") as f:
                    vb = f.read()
                os.remove(filepath)
                return await event.reply(vb, metadata={"filename": "video.mp4"})
        except Exception as e:
            print(str(e))
            return await event.reply(json.dumps({"msg": "Could not download video"}), metadata={"error": "1"})


async def main():
    async with EventPolling(handlers) as poller:
        await poller.start(0.1)


if __name__ == "__main__":
    asyncio.run(main())

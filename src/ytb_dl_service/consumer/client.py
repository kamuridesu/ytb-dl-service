import asyncio
import json
import os
from pathlib import Path
from typing import Any, Literal

import aiohttp
from Shimarin.client.events import Event, EventPolling, EventsHandlers
from yt_dlp import YoutubeDL

handlers = EventsHandlers()


def longer_than_10_minutes(info, *, incomplete):
    duration = info.get('duration')
    if duration and duration > 600:
        return 'The video is too long'


video_opts = {
    "match_filter": longer_than_10_minutes,
    "format": "best[height<=480]",
    "outtmpl": "%(title)s.%(ext)s"
}

audio_opts = {
    "match_filter": longer_than_10_minutes,
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'opus',
    }],
    'outtmpl': "%(title)s.%(ext)s",
}


async def reply(opts: dict[str, Any], url: str, event: Event):
    with YoutubeDL(opts) as ytdl:
        info = ytdl.extract_info(url, download=True)
        filepath = filepath = info['requested_downloads'][0]['filepath']
        with open(filepath, "rb") as f:
            await event.reply(f, metadata={"filename": os.path.basename(filepath)})
        Path(filepath).unlink(True)
        return


@handlers.new("new_url")
async def new_url(event: Event):
    async with aiohttp.ClientSession() as s:
        event.__session = s
        if event.payload is None:
            return await event.reply(json.dumps({"msg": "Invalid URL"}), metadata={"error": "1"})
        payload: dict[str, str] = json.loads(event.payload)
        url = payload["url"]
        kind: Literal["audio", "video"] = payload["kind"]
        try:
            if kind == "audio":
                return await reply(audio_opts, url, event)
            return await reply(video_opts, url, event)
        except Exception as e:
            print(str(e.__class__))
            print(str(e.__cause__))
            print(str(e))
            return await event.reply(json.dumps({"msg": "Could not download video"}), metadata={"error": "1"})


async def main():
    async with EventPolling(handlers) as poller:
        await poller.start(0.1)


if __name__ == "__main__":
    asyncio.run(main())

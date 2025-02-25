from io import BytesIO
import asyncio
import logging

import hypercorn

from flask import Flask, jsonify, request, send_file

from Shimarin.server.events import Event, EventEmitter, CallbackArguments, CallbackMetadata
from Shimarin.server.exceptions import EventAnswerTimeoutError
from Shimarin.plugins.flask_api import ShimaApp
import hypercorn.asyncio

from src.ytb_dl_service.producer.service import is_valid_url


app = Flask("server")
emitter = EventEmitter()
app.register_blueprint(ShimaApp(emitter, use_stream_response=False))


async def callback(params: CallbackArguments, metadata: CallbackMetadata):
    filename = "unknown.mp4"
    if metadata:
        if (metadata.get("error")):
            return jsonify(params.decode()), 500
        filename = metadata.get(filename, filename)
    return send_file(BytesIO(params), as_attachment=True, download_name=filename)


async def handler(url: str):
    event = Event("new_url", url, callback)
    await emitter.send(event)
    try:
        return (await emitter.get_answer(event.identifier, timeout=30)), 200
    except EventAnswerTimeoutError:
        return jsonify({"msg": "fail to handle request"}), 500

@app.route("/", methods=["GET"])
async def index():
    args = request.args.get("url")
    if not args or not is_valid_url(args):
        return jsonify({"msg": "url is invalid"}), 400
    re = await handler(args)
    print(re)
    return re


async def main():
    config = hypercorn.Config()
    config.bind = "0.0.0.0:8080"
    config.errorlog = "-"
    config.accesslog = "-"
    await hypercorn.asyncio.serve(app, config)


if __name__ == "__main__":
    asyncio.run(main())

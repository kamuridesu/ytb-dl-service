import asyncio
import json
from io import BytesIO

import hypercorn
import hypercorn.asyncio
from flask import Flask, Response, jsonify, request, send_file
from Shimarin.plugins.flask_api import CONTEXT_PATH, ShimaApp
from Shimarin.server.events import (
    CallbackArguments,
    CallbackMetadata,
    Event,
    EventEmitter,
)
from Shimarin.server.exceptions import EventAnswerTimeoutError

from src.ytb_dl_service.producer.service import is_valid_url

app = Flask("server")
emitter = EventEmitter()
app.register_blueprint(ShimaApp(emitter, use_stream_response=False))


async def callback(params: CallbackArguments, metadata: CallbackMetadata):
    filename = "unknown.mp4"
    if metadata:
        if (metadata.get("error")):
            return jsonify(json.loads(params.__getattribute__("decode")())), 500
        filename = metadata.get("filename", filename)
    if isinstance(params, bytes):
        if params is None:
            return jsonify({"msg": "Received NONE from consumer"}), 500
        print("Sending response file")
        return send_file(BytesIO(params), as_attachment=True, download_name=filename), 200
    return jsonify({"msg": "fail to handle bytes"}), 500


async def handler(url: str) -> tuple[Response, int]:
    event = Event("new_url", url, callback)
    await emitter.send(event)
    try:
        return (await emitter.get_answer(event.identifier, timeout=30))
    except EventAnswerTimeoutError:
        return jsonify({"msg": "fail to handle request"}), 500


@app.route(CONTEXT_PATH + "/health", methods=["GET"])
async def health():
    return "ok"


@app.route(CONTEXT_PATH + "/", methods=["GET"])
async def index():
    args = request.args.get("url")
    if not args or not is_valid_url(args):
        return jsonify({"msg": "url is invalid"}), 400
    re = await handler(args)
    return re


async def main():
    config = hypercorn.Config()
    config.bind = "0.0.0.0:8080"
    config.errorlog = "-"
    config.accesslog = "-"
    await hypercorn.asyncio.serve(app, config)


if __name__ == "__main__":
    asyncio.run(main())

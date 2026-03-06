"""Bridges ZMQ bus to websocket for explorator."""

import asyncio
import functools
import json
import logging

import zmq
import zmq.asyncio
import websockets

from config.settings import WS_HOST, WS_PORT, ZMQ_PUB_ADDR, ZMQ_SUB_ADDR, GW_SUBSCRIBE_PREFIXES

log = logging.getLogger("gateway")


clients: set[websockets.WebSocketServerProtocol] = set()


async def ws_handler(ws: websockets.WebSocketServerProtocol, zmq_pub: zmq.asyncio.Socket):
    clients.add(ws)
    remote = ws.remote_address
    log.info("client connected from %s", remote)
    try:
        async for message in ws:
            try:
                msg = json.loads(message)
                topic = msg.get("topic", "")
                data = msg.get("data", {})
                zmq_pub.send_multipart([topic.encode(), json.dumps(data).encode()])
            except (json.JSONDecodeError, AttributeError) as e:
                log.warning("bad message from client: %s", e)
    except websockets.ConnectionClosed:
        pass
    finally:
        clients.discard(ws)
        log.info("client disconnected %s", remote)


async def zmq_to_ws(ctx: zmq.asyncio.Context):
    sub = ctx.socket(zmq.SUB)
    sub.connect(ZMQ_SUB_ADDR)
    for prefix in GW_SUBSCRIBE_PREFIXES:
        sub.subscribe(prefix.encode())
    log.info("subscribed to %s on %s", [p + "*" for p in GW_SUBSCRIBE_PREFIXES], ZMQ_SUB_ADDR)

    try:
        while True:
            frames = await sub.recv_multipart()
            if len(frames) != 2:
                log.warning("expected 2-part message, got %d — skipping", len(frames))
                continue
            topic_bytes, payload_bytes = frames
            topic = topic_bytes.decode()

            try:
                data = json.loads(payload_bytes.decode())
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                log.warning("bad payload on %s: %s", topic, e)
                continue

            envelope = json.dumps({"topic": topic, "data": data})

            dead = set()
            for ws in clients:
                try:
                    await ws.send(envelope)
                except websockets.ConnectionClosed:
                    dead.add(ws)
            clients.difference_update(dead)
    finally:
        sub.close()


async def main():
    ctx = zmq.asyncio.Context()
    zmq_pub = ctx.socket(zmq.PUB)
    zmq_pub.connect(ZMQ_PUB_ADDR)
    log.info("publishing commands to %s", ZMQ_PUB_ADDR)

    handler = functools.partial(ws_handler, zmq_pub=zmq_pub)
    async with websockets.serve(handler, WS_HOST, WS_PORT):
        log.info("websocket server on ws://%s:%d", WS_HOST, WS_PORT)
        await zmq_to_ws(ctx)


if __name__ == "__main__":
    logging.basicConfig(format="%(name)s: %(message)s", level=logging.INFO)
    asyncio.run(main())

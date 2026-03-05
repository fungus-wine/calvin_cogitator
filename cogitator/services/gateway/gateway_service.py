"""Bridges ZMQ bus to websocket for explorator."""

import asyncio
import json
import sys

import zmq
import zmq.asyncio
import websockets

# This is a workaround for Python's import system — it adds the cogitator/ directory to the module
# search path so from config.settings import ... works regardless of where you run the script from.
# parents[2] walks up two directories from the file's location.exp
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from config.settings import WS_HOST, WS_PORT, ZMQ_SUB_ADDR


clients: set[websockets.WebSocketServerProtocol] = set()


async def ws_handler(ws: websockets.WebSocketServerProtocol):
    clients.add(ws)
    remote = ws.remote_address
    print(f"gateway: client connected from {remote}")
    try:
        async for _message in ws:
            # Future: parse commands from explorator and publish to ZMQ
            pass
    except websockets.ConnectionClosed:
        pass
    finally:
        clients.discard(ws)
        print(f"gateway: client disconnected {remote}")


async def zmq_to_ws():
    ctx = zmq.asyncio.Context()
    sub = ctx.socket(zmq.SUB)
    sub.connect(ZMQ_SUB_ADDR)
    sub.subscribe(b"sensor.")
    print(f"gateway: subscribed to sensor.* on {ZMQ_SUB_ADDR}")

    try:
        while True:
            topic_bytes, payload_bytes = await sub.recv_multipart()
            topic = topic_bytes.decode()
            payload = payload_bytes.decode()

            # Wrap in envelope so explorator knows the topic
            envelope = json.dumps({"topic": topic, "data": json.loads(payload)})

            dead = set()
            for ws in clients:
                try:
                    await ws.send(envelope)
                except websockets.ConnectionClosed:
                    dead.add(ws)
            clients.difference_update(dead)
    finally:
        sub.close()
        ctx.term()


async def main():
    async with websockets.serve(ws_handler, WS_HOST, WS_PORT):
        print(f"gateway: websocket server on ws://{WS_HOST}:{WS_PORT}")
        await zmq_to_ws()


if __name__ == "__main__":
    asyncio.run(main())

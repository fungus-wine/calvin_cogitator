"""Reads Teensy UART, publishes sensor data to ZMQ bus."""

import json
import time
import sys

import serial
import zmq

# This is a workaround for Python's import system — it adds the cogitator/ directory to the module
# search path so from config.settings import ... works regardless of where you run the script from.
# parents[2] walks up two directories from the file's location.
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from config.settings import (
    SERIAL_DEVICE,
    SERIAL_BAUD,
    SERIAL_RECONNECT_DELAY,
    ZMQ_PUB_ADDR,
    MESSAGE_TYPE_TO_TOPIC,
)


def open_serial(device: str, baud: int) -> serial.Serial:
    while True:
        try:
            port = serial.Serial(device, baud, timeout=0.1)
            print(f"serial: opened {device} @ {baud}")
            return port
        except serial.SerialException as exc:
            print(f"serial: {exc} — retrying in {SERIAL_RECONNECT_DELAY}s")
            time.sleep(SERIAL_RECONNECT_DELAY)


def main():
    ctx = zmq.Context()
    pub = ctx.socket(zmq.PUB)
    pub.connect(ZMQ_PUB_ADDR)
    print(f"serial: publishing to {ZMQ_PUB_ADDR}")

    port = open_serial(SERIAL_DEVICE, SERIAL_BAUD)

    try:
        while True:
            try:
                raw = port.readline()
            except serial.SerialException as exc:
                print(f"serial: lost connection — {exc}")
                port.close()
                port = open_serial(SERIAL_DEVICE, SERIAL_BAUD)
                continue

            if not raw:
                continue

            line = raw.decode("utf-8", errors="replace").strip() # turn bytes into strings
            if not line:
                continue

            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                print(f"serial: bad json: {line!r}")
                continue

            msg_type = msg.get("type")
            topic = MESSAGE_TYPE_TO_TOPIC.get(msg_type) # returns None if key is missing
            if topic is None:
                print(f"serial: unknown type: {msg_type}")
                continue

            pub.send_multipart([topic.encode(), json.dumps(msg).encode()])
    except KeyboardInterrupt:
        pass
    finally:
        port.close()
        pub.close()
        ctx.term()


if __name__ == "__main__":
    main()

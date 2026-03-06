"""Reads Teensy UART, publishes sensor data to ZMQ bus."""

import json
import logging
import time

import serial
import zmq

from config.settings import (
    SERIAL_DEVICE,
    SERIAL_BAUD,
    SERIAL_RECONNECT_DELAY,
    ZMQ_PUB_ADDR,
    MESSAGE_TYPE_TO_TOPIC,
)

log = logging.getLogger("serial")


def open_serial(device: str, baud: int) -> serial.Serial:
    while True:
        try:
            port = serial.Serial(device, baud, timeout=0.1)
            log.info("opened %s @ %d", device, baud)
            return port
        except serial.SerialException as exc:
            log.warning("%s — retrying in %ss", exc, SERIAL_RECONNECT_DELAY)
            time.sleep(SERIAL_RECONNECT_DELAY)


def main():
    ctx = zmq.Context()
    pub = ctx.socket(zmq.PUB)
    pub.connect(ZMQ_PUB_ADDR)
    log.info("publishing to %s", ZMQ_PUB_ADDR)

    port = open_serial(SERIAL_DEVICE, SERIAL_BAUD)

    try:
        while True:
            try:
                raw = port.readline()
            except serial.SerialException as exc:
                log.warning("lost connection — %s", exc)
                port.close()
                port = open_serial(SERIAL_DEVICE, SERIAL_BAUD)
                continue

            if not raw:
                continue

            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue

            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                log.warning("bad json: %r", line)
                continue

            msg_type = msg.get("type")
            topic = MESSAGE_TYPE_TO_TOPIC.get(msg_type)
            if topic is None:
                log.warning("unknown type: %s", msg_type)
                continue

            pub.send_multipart([topic.encode(), json.dumps(msg).encode()])
    except KeyboardInterrupt:
        pass
    finally:
        port.close()
        pub.close()
        ctx.term()


if __name__ == "__main__":
    logging.basicConfig(format="%(name)s: %(message)s", level=logging.INFO)
    main()

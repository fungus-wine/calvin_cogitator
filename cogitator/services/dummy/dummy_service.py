"""Generates fake sensor data and publishes to ZMQ bus — drop-in replacement for serial service."""

import json
import logging
import math
import random
import time

import zmq

from config.settings import (
    ZMQ_PUB_ADDR, ZMQ_SUB_ADDR, MESSAGE_TYPE_TO_TOPIC,
    TOPIC_CMD_PID, TOPIC_RSP_PID, TOPIC_CMD_PID_READ, TOPIC_RSP_PID_READ,
)

log = logging.getLogger("dummy")

PUBLISH_HZ = 50  # roughly match real IMU rate

# Default PID values returned for read requests in dummy mode
DEFAULT_PID = {
    "inner": {"kp": 1.0, "ki": 0.0, "kd": 0.0},
    "outer": {"kp": 1.0, "ki": 0.0, "kd": 0.0},
}


def generate_imu(t: float) -> dict:
    """Simulate a balancing robot with gentle oscillation."""
    return {
        "type": "imu",
        "ax": 0.05 * math.sin(t * 2) + random.gauss(0, 0.01),
        "ay": random.gauss(0, 0.01),
        "az": 9.81 + random.gauss(0, 0.02),
        "gx": 0.3 * math.sin(t * 3) + random.gauss(0, 0.05),
        "gy": random.gauss(0, 0.05),
        "gz": random.gauss(0, 0.02),
    }


def generate_tof(t: float) -> dict:
    """Simulate slowly varying distance readings."""
    return {
        "type": "tof",
        "front": int(300 + 150 * math.sin(t * 0.5) + random.gauss(0, 5)),
        "rear": int(400 + 100 * math.cos(t * 0.3) + random.gauss(0, 5)),
    }


def generate_i2c_health() -> dict:
    """Mostly zeros with rare glitches."""
    return {
        "type": "i2c_health",
        "nacks": 1 if random.random() < 0.01 else 0,
        "timeouts": 1 if random.random() < 0.005 else 0,
        "resets": 0,
    }


def main():
    ctx = zmq.Context()

    pub = ctx.socket(zmq.PUB)
    pub.connect(ZMQ_PUB_ADDR)

    sub = ctx.socket(zmq.SUB)
    sub.connect(ZMQ_SUB_ADDR)
    sub.subscribe(TOPIC_CMD_PID.encode())
    sub.subscribe(TOPIC_CMD_PID_READ.encode())

    poller = zmq.Poller()
    poller.register(sub, zmq.POLLIN)

    log.info("publishing to %s at ~%d Hz", ZMQ_PUB_ADDR, PUBLISH_HZ)
    log.info("listening for %s commands", TOPIC_CMD_PID)

    interval = 1.0 / PUBLISH_HZ
    tick = 0
    next_tick = time.monotonic()

    try:
        while True:
            t = time.monotonic()

            # IMU every tick
            msg = generate_imu(t)
            topic = MESSAGE_TYPE_TO_TOPIC[msg["type"]]
            pub.send_multipart([topic.encode(), json.dumps(msg).encode()])

            # ToF every 5th tick (~10 Hz)
            if tick % 5 == 0:
                msg = generate_tof(t)
                topic = MESSAGE_TYPE_TO_TOPIC[msg["type"]]
                pub.send_multipart([topic.encode(), json.dumps(msg).encode()])

            # I2C health every 50th tick (~1 Hz)
            if tick % 50 == 0:
                msg = generate_i2c_health()
                topic = MESSAGE_TYPE_TO_TOPIC[msg["type"]]
                pub.send_multipart([topic.encode(), json.dumps(msg).encode()])

            # Check for incoming commands (non-blocking)
            events = dict(poller.poll(0))
            if sub in events:
                topic_bytes, payload_bytes = sub.recv_multipart()
                cmd_topic = topic_bytes.decode()
                data = json.loads(payload_bytes.decode())

                if cmd_topic == TOPIC_CMD_PID:
                    log.info("got PID command: %s", data)
                    response = {**data, "status": "confirmed"}
                    pub.send_multipart([TOPIC_RSP_PID.encode(), json.dumps(response).encode()])
                elif cmd_topic == TOPIC_CMD_PID_READ:
                    log.info("got PID read request")
                    pub.send_multipart([TOPIC_RSP_PID_READ.encode(), json.dumps(DEFAULT_PID).encode()])

            tick += 1
            next_tick += interval
            time.sleep(max(0, next_tick - time.monotonic()))
    except KeyboardInterrupt:
        pass
    finally:
        sub.close()
        pub.close()
        ctx.term()


if __name__ == "__main__":
    logging.basicConfig(format="%(name)s: %(message)s", level=logging.INFO)
    main()

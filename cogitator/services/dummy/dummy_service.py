"""Generates fake sensor data and publishes to ZMQ bus — drop-in replacement for serial service."""

import json
import math
import random
import sys
import time

import zmq

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from config.settings import ZMQ_PUB_ADDR, MESSAGE_TYPE_TO_TOPIC

PUBLISH_HZ = 50  # roughly match real IMU rate


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
    print(f"dummy: publishing to {ZMQ_PUB_ADDR} at ~{PUBLISH_HZ} Hz")

    interval = 1.0 / PUBLISH_HZ
    tick = 0

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

            tick += 1
            time.sleep(interval)
    except KeyboardInterrupt:
        pass
    finally:
        pub.close()
        ctx.term()


if __name__ == "__main__":
    main()

"""PID tuning service — receives tuning commands, forwards to instinctus, publishes confirmations."""

import json
import logging

import zmq

from config.settings import (
    ZMQ_PUB_ADDR, ZMQ_SUB_ADDR,
    TOPIC_CMD_PID, TOPIC_RSP_PID, TOPIC_CMD_PID_READ, TOPIC_RSP_PID_READ,
)

log = logging.getLogger("pid")

VALID_LOOPS = {"inner", "outer"}
VALID_PARAMS = {"kp", "ki", "kd"}


def validate(data: dict) -> str | None:
    """Return error string if invalid, None if ok."""
    loop = data.get("loop")
    if loop not in VALID_LOOPS:
        return f"invalid loop: {loop!r}, expected inner or outer"
    for param in VALID_PARAMS:
        val = data.get(param)
        if not isinstance(val, (int, float)):
            return f"missing or invalid {param}: {val!r}"
    return None


def main():
    ctx = zmq.Context()

    sub = ctx.socket(zmq.SUB)
    sub.connect(ZMQ_SUB_ADDR)
    sub.subscribe(TOPIC_CMD_PID.encode())
    sub.subscribe(TOPIC_CMD_PID_READ.encode())

    pub = ctx.socket(zmq.PUB)
    pub.connect(ZMQ_PUB_ADDR)

    log.info("listening for %s commands", TOPIC_CMD_PID)

    try:
        while True:
            topic_bytes, payload = sub.recv_multipart()
            cmd_topic = topic_bytes.decode()
            data = json.loads(payload.decode())

            if cmd_topic == TOPIC_CMD_PID_READ:
                # TODO: query instinctus for current PID values via serial
                log.info("read request (no serial target yet)")
                response = {"status": "error", "error": "no serial target (instinctus not ready)"}
                pub.send_multipart([TOPIC_RSP_PID_READ.encode(), json.dumps(response).encode()])
                continue

            err = validate(data)
            if err:
                log.warning("validation error: %s", err)
                response = {**data, "status": "error", "error": err}
            else:
                # TODO: send to instinctus via serial and wait for confirmation
                # For now, instinctus has no PID tuning code, so this is a placeholder.
                # In --dummy mode the dummy service handles the echo-back instead.
                log.info("received %s loop params (no serial target yet)", data["loop"])
                response = {**data, "status": "error", "error": "no serial target (instinctus not ready)"}

            pub.send_multipart([TOPIC_RSP_PID.encode(), json.dumps(response).encode()])
    except KeyboardInterrupt:
        pass
    finally:
        sub.close()
        pub.close()
        ctx.term()


if __name__ == "__main__":
    logging.basicConfig(format="%(name)s: %(message)s", level=logging.INFO)
    main()

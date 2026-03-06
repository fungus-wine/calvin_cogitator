"""XPUB/XSUB broker — central hub for all ZMQ traffic."""

import logging

import zmq
from config.settings import ZMQ_PUB_SIDE, ZMQ_SUB_SIDE

log = logging.getLogger("broker")


def main():
    ctx = zmq.Context()
    pub_side = ctx.socket(zmq.XSUB)
    pub_side.bind(ZMQ_PUB_SIDE)
    sub_side = ctx.socket(zmq.XPUB)
    sub_side.bind(ZMQ_SUB_SIDE)
    log.info("XSUB on %s, XPUB on %s", ZMQ_PUB_SIDE, ZMQ_SUB_SIDE)
    try:
        zmq.proxy(pub_side, sub_side)
    except KeyboardInterrupt:
        pass
    finally:
        pub_side.close()
        sub_side.close()
        ctx.term()


if __name__ == "__main__":
    logging.basicConfig(format="%(name)s: %(message)s", level=logging.INFO)
    main()
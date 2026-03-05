"""XPUB/XSUB broker — central hub for all ZMQ traffic."""

import zmq
from config.settings import ZMQ_PUB_SIDE, ZMQ_SUB_SIDE


def main():
    ctx = zmq.Context()
    pub_side = ctx.socket(zmq.XSUB)
    pub_side.bind(ZMQ_PUB_SIDE)
    sub_side = ctx.socket(zmq.XPUB)
    sub_side.bind(ZMQ_SUB_SIDE)
    print(f"broker: XSUB on {ZMQ_PUB_SIDE}, XPUB on {ZMQ_SUB_SIDE}")
    try:
        zmq.proxy(pub_side, sub_side)
    except KeyboardInterrupt:
        pass
    finally:
        pub_side.close()
        sub_side.close()
        ctx.term()


if __name__ == "__main__":
    main()
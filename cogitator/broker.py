"""XPUB/XSUB broker — central hub for all ZMQ traffic."""

import zmq
from config.settings import ZMQ_FRONTEND, ZMQ_BACKEND


def main():
    ctx = zmq.Context()
    frontend = ctx.socket(zmq.XSUB)
    frontend.bind(ZMQ_FRONTEND)
    backend = ctx.socket(zmq.XPUB)
    backend.bind(ZMQ_BACKEND)
    print(f"broker: XSUB on {ZMQ_FRONTEND}, XPUB on {ZMQ_BACKEND}")
    try:
        zmq.proxy(frontend, backend)
    except KeyboardInterrupt:
        pass
    finally:
        frontend.close()
        backend.close()
        ctx.term()


if __name__ == "__main__":
    main()

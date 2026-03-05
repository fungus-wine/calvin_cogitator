# Docker Cheat Sheet for Calvin

## First Time Setup

```bash
docker run -it --runtime nvidia \
  --name calvin \
  --network host \
  --privileged \
  --device=/dev/bus/usb \
  -v ~/code:/workspace \
  -v ~/config/starship.toml:/root/.config/starship.toml \
  -v ~/config/bashrc:/root/.bashrc \
  -v jetson-pip:/usr/local \
  -v jetson-pip-cache:/root/.cache/pip \
  dustynv/pytorch:2.7-r36.4.0-cu128-24.04
```

## Day-to-Day Usage

| Command | What it does |
|---|---|
| `docker start -i calvin` | Start and attach to the container |
| `exit` | Stop the container (from inside) |
| `docker stop calvin` | Stop the container (from outside) |
| `docker exec -it calvin bash` | Open a second shell in a running container |

## What Survives What

| | `stop` + `start` | `rm` + `run` |
|---|---|---|
| Python packages | Yes (volume) | Yes (volume) |
| Code in ~/code | Yes (bind mount) | Yes (bind mount) |
| Starship binary | Yes | Yes (lives in /usr/local volume) |
| Starship config | Yes (bind mount) | Yes (bind mount) |
| .bashrc | Yes (bind mount) | Yes (bind mount) |
| Other container changes | Yes | **No** |

## When Do I Need to `rm` + `run`?

Only when you need to change `docker run` flags (add a volume, change the image, etc.):

```bash
docker stop calvin
docker rm calvin
docker run ...   # with new flags
```

## Networking

The container uses `--network host`, so it shares the Jetson's network directly.
Any port a service listens on is accessible at the Jetson's IP — no port mapping needed.

From your Mac: `ws://<jetson-ip>:5560`

## Running Cogitator

```bash
cd /workspace/calvin_cogitator/cogitator
./run.sh          # real serial from Teensy
./run.sh --dummy  # fake sensor data for testing
```

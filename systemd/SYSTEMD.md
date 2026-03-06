# Cogitator Systemd Cheatsheet

## Install

```bash
# Deploy with real serial (Teensy connected):
sudo ./systemd/install.sh

# Deploy in dummy/test mode (fake sensor data):
sudo ./systemd/install.sh --dummy
```

This copies `cogitator/` to `/opt/cogitator`, installs the unit files, and starts the appropriate services. Re-run to switch modes.

## Services

| Unit | Description | Mode |
|------|-------------|------|
| `cogitator-broker` | ZMQ XPUB/XSUB broker | both |
| `cogitator-serial` | Teensy UART reader | real |
| `cogitator-pid` | PID tuning relay | real |
| `cogitator-dummy` | Fake sensor data + PID echo | dummy |
| `cogitator-gateway` | ZMQ-to-WebSocket bridge | both |

## Status

```bash
# All services at a glance
systemctl status cogitator-*

# One service in detail
systemctl status cogitator-gateway
```

## Logs

```bash
# Tail logs for one service
journalctl -u cogitator-gateway -f

# Tail all cogitator logs together
journalctl -u 'cogitator-*' -f

# Logs since last boot
journalctl -u cogitator-serial -b

# Last 50 lines
journalctl -u cogitator-broker -n 50
```

## Start / Stop / Restart

```bash
# Restart a single service
sudo systemctl restart cogitator-serial

# Stop everything
sudo systemctl stop cogitator-broker cogitator-serial cogitator-pid cogitator-gateway

# Start everything (real mode)
sudo systemctl start cogitator-broker cogitator-serial cogitator-pid cogitator-gateway
```

## Switch Modes

```bash
# Switch to dummy mode
sudo systemctl stop cogitator-serial cogitator-pid
sudo systemctl start cogitator-dummy

# Switch back to real mode
sudo systemctl stop cogitator-dummy
sudo systemctl start cogitator-serial cogitator-pid
```

Or just re-run `sudo ./systemd/install.sh [--dummy]`.

## Boot Behavior

Services are enabled at install time and start automatically on boot. To disable:

```bash
sudo systemctl disable cogitator-broker cogitator-serial cogitator-pid cogitator-gateway
```

# Calvin Cogitator - Project Instructions

## System Overview

**Calvin Cogitator** is the high-level intelligence system for Calvin, a self-balancing robot. Running on a Jetson Orin Nano, it provides advanced AI capabilities including object recognition, motion planning, video/audio streaming, and LLM-based decision making.

**Calvin's Three-System Architecture:**
- **instinctus** - Low-level reflexes and motor control- `/Users/damoncali/code/arduino/calvin_instinctus/CLAUDE.md`
- **cogitator** (THIS SYSTEM) - High-level thinking and AI (Jetson Orin Nano)
- **explorator** - Human monitoring interface (Electron app) - `/Users/damoncali/code/calvin_explorator/CLAUDE.md`

**Integration:**
- Receives status from instinctus M7 core via serial
- Sends commands to instinctus M7 core via serial
- Streams telemetry to explorator via network
- Receives user commands from explorator via network

## Jetson Orin Nano Platform

**Hardware:**
- CPU: 6-core ARM Cortex-A78AE @ 1.5 GHz
- GPU: 1024-core NVIDIA Ampere with 32 Tensor Cores
- Memory: 8GB LPDDR5
- Storage: microSD + NVMe SSD (recommended)
- USB: 4x USB 3.2, 1x USB-C
- Network: Gigabit Ethernet, M.2 WiFi
- GPIO: 40-pin header (UART, I2C, SPI, GPIO)

**Peripherals:**
- OAK-D Pro W camera (stereo depth, object detection, built-in IMU)
- USB or GPIO UART connection to Teensy 4.1

## Responsibilities (THIS SYSTEM)

**High-Level Intelligence:**
- Object recognition and tracking
- Motion planning and path finding
- Visual SLAM and navigation
- Sensor fusion from multiple sources
- LLM interface for natural language control
- High-level decision making and goal planning

**Communication Hub:**
- Serial communication with instinctus
- Network communication with explorator
- Video/audio streaming to explorator
- Telemetry aggregation and forwarding

## Project Structure

```
calvin_cogitator/
├── requirements.txt          # pyzmq, pyserial, websockets
├── cogitator/
│   ├── run.sh                # Process launcher (--dummy flag for fake data)
│   ├── broker.py             # ZMQ XPUB/XSUB broker (central message hub)
│   ├── test.html             # WebSocket gateway test page
│   ├── config/
│   │   └── settings.py       # ZMQ addresses, WS config, serial config, topic names
│   └── services/
│       ├── gateway/
│       │   └── gateway_service.py   # Bridges ZMQ bus ↔ WebSocket (for explorator)
│       ├── serial/
│       │   └── serial_service.py    # Reads Teensy UART, publishes to ZMQ bus
│       └── dummy/
│           └── dummy_service.py     # Generates fake sensor data for testing
```

## Architecture

- **ZMQ Broker** (`broker.py`): XPUB/XSUB proxy on ports 5550/5551 — all services publish/subscribe through it
- **Serial Service**: Reads JSON messages from Teensy over UART, maps message types to ZMQ topics (`sensor.imu`, `sensor.tof`, `sensor.i2c_health`)
- **Gateway Service**: Bridges ZMQ subscriptions to WebSocket on port 5560 for explorator
- **Dummy Service**: Replaces serial service with synthetic data for development/testing
- **run.sh**: Launches broker + gateway + serial (or `--dummy`) as background processes

## Message Format (initial, simple)
Teensy sends newline-delimited JSON. Serial service republishes as-is with a topic prefix.

```json
{"type": "imu", "ax": 0.1, "ay": -0.02, "az": 9.8, "gx": 0.5, "gy": -0.1, "gz": 0.0}
{"type": "tof", "front": 250, "rear": 180}
{"type": "i2c_health", "nacks": 0, "timeouts": 0, "resets": 0}
```

## Implementation Plan

**Phase 1: (Complete)**
- ZMQ broker
- Gateway service (ZMQ bus → WebSocket)
- Serial service (Teensy UART → ZMQ bus)
- Dummy service (fake sensor data for testing)
- test.html for gateway testing



**Phase 2: (TBD)**
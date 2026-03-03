# Calvin Cogitator - Sensor Streaming Bringup Plan

## Context
Get Teensy sensor data (IMU, ToF, I2C health) flowing through the Jetson to explorator for real-time visualization. Build on a ZMQ-based service architecture that supports future additions (OAK-D video, ReSpeaker audio, AI planner) without restructuring.

## Architecture

```
Teensy --serial--> [Jetson: serial service --ZMQ--> broker <--ZMQ-- gateway] --websocket--> Explorator
```

### Three Layers
1. **Device services** — one per hardware source, publish to ZMQ bus
2. **ZMQ bus** — internal pub/sub, topic-based routing, XPUB/XSUB broker
3. **Gateway** — bridges ZMQ to websocket for explorator

### Ports
- **5550**: ZMQ broker (internal to Jetson only)
- **5560**: Websocket server (network-facing, explorator connects here)

### Topics (initial)
- `sensor.imu` — accel, gyro data from ICM20948
- `sensor.tof` — front/rear distance from VL53L4CX sensors
- `sensor.i2c_health` — error counts, NACK counts, timeouts

### Future Topics (no work needed now, just reserved naming)
- `video.rgb`, `video.depth` — OAK-D Pro W
- `audio.chunk` — ReSpeaker
- `command.*` — explorator → Teensy commands

## Project Structure

```
cogitator/
├── broker.py                  # ~10 line XPUB/XSUB proxy
├── config/
│   └── settings.py            # Ports, baud rate, serial device, topic names
├── services/
│   ├── serial/
│   │   └── serial_service.py  # Reads Teensy UART, publishes sensor topics
│   └── gateway/
│       └── gateway_service.py # ZMQ subscriber → websocket server
└── run.sh                     # Starts broker, then services
```

## Implementation Steps

### Step 1: Config
**File:** `config/settings.py`  

- ZMQ broker address: `tcp://localhost:5550`
- Websocket port: `5560`
- Serial device: `/dev/ttyACM0` (or whatever the Teensy enumerates as)
- Serial baud: `115200`
- Topic names as constants

### Step 2: ZMQ Broker
**File:** `broker.py`

- XPUB/XSUB proxy — binds frontend and backend sockets
- ~10 lines of Python
- Starts first, services connect to it
- Services can start/stop in any order without issues

### Step 3: Serial Service
**File:** `services/serial/serial_service.py`

- Opens Teensy serial port with pyserial
- Reads newline-delimited JSON
- Parses each line, determines topic from message type
- Publishes to ZMQ with appropriate topic prefix
- Handles serial disconnects gracefully (reconnect loop)

### Step 4: Gateway Service
**File:** `services/gateway/gateway_service.py`

- Subscribes to all `sensor.*` topics on ZMQ
- Opens websocket server on port 5560
- Forwards ZMQ messages to all connected websocket clients
- Receives messages from websocket clients and publishes to ZMQ (for future commands)
- Handles client connect/disconnect gracefully

### Step 5: Launcher
**File:** `run.sh`

- Starts broker first
- Brief pause for broker to bind
- Starts serial service and gateway service
- Traps SIGINT to shut everything down cleanly

## Dependencies
- `pyzmq` — ZMQ bindings
- `pyserial` — serial port access
- `websockets` or `fastapi` + `uvicorn` — websocket server

## Verification
1. Teensy streaming sensor JSON over USB serial — confirm with `screen` or `minicom`
2. Start broker + serial service — confirm ZMQ messages with a simple subscriber test script
3. Start gateway — connect from browser/wscat to `ws://jetson-ip:5560`, confirm sensor data flowing
4. Connect explorator — confirm real-time data in UI

## Message Format (initial, simple)
Teensy sends newline-delimited JSON. Serial service republishes as-is with a topic prefix.

```json
{"type": "imu", "ax": 0.1, "ay": -0.02, "az": 9.8, "gx": 0.5, "gy": -0.1, "gz": 0.0}
{"type": "tof", "front": 250, "rear": 180}
{"type": "i2c_health", "nacks": 0, "timeouts": 0, "resets": 0}
```

## Deferred
- OAK-D service (video.rgb, video.depth)
- ReSpeaker service (audio.chunk)
- AI planner service
- Command routing from explorator → Teensy
- Authentication/security on websocket (if needed)
- Systemd/supervisord for production service management

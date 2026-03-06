import os

# ZMQ broker
ZMQ_PUB_SIDE = os.environ.get("COG_ZMQ_PUB_SIDE", "tcp://*:5550")       # services connect here to publish
ZMQ_SUB_SIDE = os.environ.get("COG_ZMQ_SUB_SIDE", "tcp://*:5551")       # subscribers connect here
ZMQ_PUB_ADDR = os.environ.get("COG_ZMQ_PUB_ADDR", "tcp://localhost:5550")
ZMQ_SUB_ADDR = os.environ.get("COG_ZMQ_SUB_ADDR", "tcp://localhost:5551")

# Websocket gateway
WS_HOST = os.environ.get("COG_WS_HOST", "0.0.0.0")
WS_PORT = int(os.environ.get("COG_WS_PORT", "5560"))

# Serial
SERIAL_DEVICE = os.environ.get("COG_SERIAL_DEVICE", "/dev/ttyACM0")
SERIAL_BAUD = int(os.environ.get("COG_SERIAL_BAUD", "115200"))
SERIAL_RECONNECT_DELAY = float(os.environ.get("COG_SERIAL_RECONNECT_DELAY", "2.0"))

# Topic names
TOPIC_IMU = "sensor.imu"
TOPIC_TOF = "sensor.tof"
TOPIC_I2C_HEALTH = "sensor.i2c_health"
TOPIC_CMD_PID = "command.pid"
TOPIC_RSP_PID = "response.pid"
TOPIC_CMD_PID_READ = "command.pid.read"
TOPIC_RSP_PID_READ = "response.pid.read"

# Topic prefixes the gateway forwards to explorator
GW_SUBSCRIBE_PREFIXES = ["sensor.", "response."]

# Map Teensy message "type" field to ZMQ topic
MESSAGE_TYPE_TO_TOPIC = {
    "imu": TOPIC_IMU,
    "tof": TOPIC_TOF,
    "i2c_health": TOPIC_I2C_HEALTH,
}

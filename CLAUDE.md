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

## Impelementation Plan

**Phase 1: (Complete)**
- create ZMQ broker
- create gateway service (Bridges ZMQ bus to websocket)
- create serial service (Reads Teensy UART, publishes sensor data to ZMQ bus)
- create dummy service (generates fake data to mimic Teensy for testing)
- crate test.html to test gateway

**Phase 2: (TBD)**
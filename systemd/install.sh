#!/usr/bin/env bash
# Installs cogitator systemd units on the Jetson.
# Usage: sudo ./install.sh [--dummy]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
INSTALL_DIR="/opt/cogitator"

# Copy application code
echo "copying cogitator to $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
rsync -a --delete "$REPO_DIR/cogitator/" "$INSTALL_DIR/"

# Install unit files
echo "installing systemd units"
cp "$SCRIPT_DIR"/cogitator-*.service /etc/systemd/system/
systemctl daemon-reload

# Enable and start services
if [[ "${1:-}" == "--dummy" ]]; then
    echo "enabling dummy mode"
    systemctl disable --now cogitator-serial.service cogitator-pid.service 2>/dev/null || true
    systemctl enable --now cogitator-broker.service cogitator-dummy.service cogitator-gateway.service
else
    echo "enabling real mode"
    systemctl disable --now cogitator-dummy.service 2>/dev/null || true
    systemctl enable --now cogitator-broker.service cogitator-serial.service cogitator-pid.service cogitator-gateway.service
fi

echo "done. check status with: systemctl status cogitator-*"

#!/bin/bash
THRESHOLD=${1:-36}
HYSTERESIS=${2:-2}
DELAY=${3:-2}
SERVICE_PATH=/etc/systemd/system/pimoroni-fanshim.service

read -r -d '' UNIT_FILE << EOF
[Unit]
Description=Fan Shim Service
After=multi-user.target

[Service]
Type=simple
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/automatic.py --threshold $THRESHOLD --hysteresis $HYSTERESIS --delay $DELAY
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

echo "Installing psutil"
pip3 install psutil

echo "Installing service to: $SERVICE_PATH"
echo "$UNIT_FILE" > $SERVICE_PATH
systemctl daemon-reload
systemctl enable pimoroni-fanshim.service
systemctl start pimoroni-fanshim.service
systemctl status pimoroni-fanshim.service

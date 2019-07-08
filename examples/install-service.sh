#!/bin/bash
THRESHOLD=36
HYSTERESIS=2
DELAY=2
PREEMPT="no"
SERVICE_PATH=/etc/systemd/system/pimoroni-fanshim.service

while [[ $# -gt 0 ]]; do
	K="$1"
	case $K in
		-p|--preempt)
		if [ "$2" == "yes" ] || [ "$2" == "no"]; then
			PREEMPT="$2"
			shift
		else
			PREEMPT="yes"
		fi
		shift
		;;
		-t|--threshold)
		THRESHOLD="$2"
		shift
		shift
		;;
		-h|--hysteresis)
		HYSTERESIS="$2"
		shift
		shift
		;;
		-d|--delay)
		DELAY="$2"
		shift
		shift
		;;
		*)
		shift
	esac
done

if [ "$PREEMPT" == "yes" ]; then
    DO_PREEMPT='--preempt'
fi

cat << EOF
Setting up with:
Threshold: $THRESHOLD C
Hysteresis: $HYSTERESIS C
Delay: $DELAY seconds
Preempt: $PREEMPT

To change these options, run:
sudo ./install-service --threshold <n> --hysteresis <n> --delay <n> (--preempt)

Or edit: $SERVICE_PATH


EOF

read -r -d '' UNIT_FILE << EOF
[Unit]
Description=Fan Shim Service
After=multi-user.target

[Service]
Type=simple
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/automatic.py --threshold $THRESHOLD --hysteresis $HYSTERESIS --delay $DELAY $DO_PREEMPT
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

printf "Checking for psutil\n"
python3 - <<EOF
import psutil
EOF
if [ $? -ne 0 ]; then
	printf "Installing psutil\n"
	pip3 install psutil fanshim
else
	printf "psutil already installed\n"
fi

printf "\nInstalling service to: $SERVICE_PATH\n"
echo "$UNIT_FILE" > $SERVICE_PATH
systemctl daemon-reload
systemctl enable --no-pager pimoroni-fanshim.service
systemctl start --no-pager pimoroni-fanshim.service
systemctl status --no-pager pimoroni-fanshim.service

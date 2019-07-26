#!/bin/bash
ON_THRESHOLD=65
OFF_THRESHOLD=55
HYSTERESIS=5
DELAY=2
PREEMPT="no"
POSITIONAL_ARGS=()
NOLED="no"
NOBUTTON="no"

OLD_THRESHOLD=""
OLD_HYSTERESIS=""

SERVICE_PATH=/etc/systemd/system/pimoroni-fanshim.service

if ! [ -f "/usr/bin/python3" ]; then
	printf "Fan SHIM controller requires Python 3\n"
	printf "You should run: 'sudo apt install python3'\n"
	exit 1
fi

if ! [ -f "/usr/bin/pip3" ]; then
	printf "Fan SHIM controller requires Python 3 pip\n"
	printf "You should run: 'sudo apt install python3-pip'\n"
	exit 1
fi

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
	-l|--noled)
		if [ "$2" == "yes" ] || [ "$2" == "no"]; then
			NOLED="$2"
			shift
		else
			NOLED="yes"
		fi
		shift
		;;
	-b|--nobutton)
		if [ "$2" == "yes" ] || [ "$2" == "no"]; then
			NOBUTTON="$2"
			shift
		else
			NOBUTTON="yes"
		fi
		shift
		;;
        --on-threshold)
		ON_THRESHOLD="$2"
		shift
		shift
		;;
	--off-threshold)
		OFF_THRESHOLD="$2"
		shift
		shift
		;;
	-t|--threshold)
		OLD_THRESHOLD="error"
		shift
		shift
		;;
	-h|--hysteresis)
		OLD_HYSTERESIS="error"
		shift
		shift
		;;
	-d|--delay)
		DELAY="$2"
		shift
		shift
		;;
	*)
		POSITIONAL_ARGS+=("$1")
		shift
	esac
done

set -- "${POSITIONAL_ARGS[@]}"

EXTRA_ARGS=""

if [ "$OLD_THRESHOLD" == "error" ] || [ "$OLD_HYSTERESIS" == "error" ]; then
	printf "The --threshold and --hysteresis parameters are deprecated.\n"
	printf "Use --off-threshold and --on-threshold instead.\n"
	exit 1
fi

if [ "$PREEMPT" == "yes" ]; then
	EXTRA_ARGS+=' --preempt'
fi

if [ "$NOLED" == "yes" ]; then
	EXTRA_ARGS+=' --noled'
fi

if [ "$NOBUTTON" == "yes" ]; then
	EXTRA_ARGS+=' --nobutton'
fi

if ! [ "$1" == "" ]; then
	THRESHOLD=$1
fi

if ! [ "$2" == "" ]; then
	HYSTERESIS=$2
fi


cat << EOF
Setting up with:
Off Threshold: $OFF_THRESHOLD C
On Threshold: $ON_THRESHOLD C
Delay: $DELAY seconds
Preempt: $PREEMPT
No LED: $NOLED
No Button: $NOBUTTON

To change these options, run:
sudo ./install-service.sh --off-threshold <n> --on-threshold <n> --delay <n> (--preempt) (--noled) (--nobutton)

Or edit: $SERVICE_PATH


EOF

read -r -d '' UNIT_FILE << EOF
[Unit]
Description=Fan Shim Service
After=multi-user.target

[Service]
Type=simple
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/automatic.py --on-threshold $ON_THRESHOLD --off-threshold $OFF_THRESHOLD --delay $DELAY $EXTRA_ARGS
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

printf "Checking for rpi.gpio>=0.7.0a2 (for Pi 4 support)\n"
python3 - <<EOF
import RPi.GPIO as GPIO
from pkg_resources import parse_version
import sys
if parse_version(GPIO.VERSION) < parse_version('0.7.0a2'):
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
	printf "Installing rpi.gpio\n"
	pip3 install --upgrade --pre rpi.gpio
else
	printf "rpi.gpio >= 0.7.0a2 already installed\n"
fi

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
systemctl restart --no-pager pimoroni-fanshim.service
systemctl status --no-pager pimoroni-fanshim.service

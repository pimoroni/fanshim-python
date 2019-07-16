#!/bin/bash
THRESHOLD=55
HYSTERESIS=5
DELAY=2
PREEMPT="no"
POSITIONAL_ARGS=()
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
		POSITIONAL_ARGS+=("$1")
		shift
	esac
done

set -- "${POSITIONAL_ARGS[@]}"

EXTRA_ARGS=""

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
Threshold: $THRESHOLD C
Hysteresis: $HYSTERESIS C
Delay: $DELAY seconds
Preempt: $PREEMPT
No LED: $NOLED
No Button: $NOBUTTON

To change these options, run:
sudo ./install-service.sh --threshold <n> --hysteresis <n> --delay <n> (--preempt) (--noled) (--nobutton)

Or edit: $SERVICE_PATH


EOF

read -r -d '' UNIT_FILE << EOF
[Unit]
Description=Fan Shim Service
After=multi-user.target

[Service]
Type=simple
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/automatic.py --threshold $THRESHOLD --hysteresis $HYSTERESIS --delay $DELAY $EXTRA_ARGS
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
systemctl restart --no-pager pimoroni-fanshim.service
systemctl status --no-pager pimoroni-fanshim.service

#!/bin/bash
ON_THRESHOLD=65
OFF_THRESHOLD=55
HYSTERESIS=5
DELAY=2
PREEMPT="no"
POSITIONAL_ARGS=()
NOLED="no"
NOBUTTON="no"
BRIGHTNESS=255
PYTHON="python3"
PIP="pip3"

ON_THRESHOLD_SET=false
OFF_THRESHOLD_SET=false
VENV_SET=false

OLD_THRESHOLD=""
OLD_HYSTERESIS=""

SERVICE_PATH=/etc/systemd/system/pimoroni-fanshim.service

USAGE="sudo ./install-service.sh --off-threshold <n> --on-threshold <n> --delay <n> --brightness <n> --venv <python_virtual_environment> (--preempt) (--noled) (--nobutton)"

while [[ $# -gt 0 ]]; do
	K="$1"
	case $K in
	-p|--preempt)
		if [ "$2" == "yes" ] || [ "$2" == "no" ]; then
			PREEMPT="$2"
			shift
		else
			PREEMPT="yes"
		fi
		shift
		;;
	-l|--noled)
		if [ "$2" == "yes" ] || [ "$2" == "no" ]; then
			NOLED="$2"
			shift
		else
			NOLED="yes"
		fi
		shift
		;;
	-b|--nobutton)
		if [ "$2" == "yes" ] || [ "$2" == "no" ]; then
			NOBUTTON="$2"
			shift
		else
			NOBUTTON="yes"
		fi
		shift
		;;
	-o|--on-threshold)
		ON_THRESHOLD="$2"
		ON_THRESHOLD_SET=true
		shift
		shift
		;;
	-f|--off-threshold)
		OFF_THRESHOLD="$2"
		OFF_THRESHOLD_SET=true
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
	-r|--brightness)
		BRIGHTNESS="$2"
		shift
		shift
		;;
	--venv)
		VENV="$(realpath ${2%/})/bin"
		VENV_SET=true
		PYTHON="$VENV/python3"
		PIP="$VENV/pip3"
		shift
		shift
		;;
	*)
		if [[ $1 == -* ]]; then
			printf "Unrecognised option: $1\n";
			printf "Usage: $USAGE\n";
			exit 1
		fi
		POSITIONAL_ARGS+=("$1")
		shift
	esac
done

if ! ( type -P $PYTHON > /dev/null ) ; then
	if [ $VENV_SET ]; then
		printf "Cannot find virtual environment.\n"
		printf "Set to base of virtual environment i.e. <venv>/bin/python3.\n"
	else
		printf "Fan SHIM controller requires Python 3\n"
		printf "You should run: 'sudo apt install python3'\n"
	fi
	exit 1
fi

if ! ( type -P $PIP > /dev/null ) ; then
	printf "Fan SHIM controller requires Python 3 pip\n"
	if [ $VENV_SET ]; then
		printf "Ensure that your virtual environment has pip3 installed.\n"
	else
		printf "You should run: 'sudo apt install python3-pip'\n"
	fi
	exit 1
fi

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
	if [ $ON_THRESHOLD_SET ]; then
		printf "Refusing to overwrite explicitly set On Threshold ($ON_THRESHOLD) with positional argument!\n"
		printf "Please double-check your arguments and use one or the other!\n"
		exit 1
	fi
	ON_THRESHOLD=$1
fi

if ! [ "$2" == "" ]; then
	if [ $OFF_THRESHOLD_SET ]; then
		printf "Refusing to overwrite explicitly set Off Threshold ($OFF_THRESHOLD) with positional argument!\n"
		printf "Please double-check your arguments and use one or the other!\n"
		exit 1
	fi
	(( OFF_THRESHOLD = ON_THRESHOLD - $2 ))
fi


cat << EOF
Setting up with:
Off Threshold:  $OFF_THRESHOLD C
On Threshold:   $ON_THRESHOLD C
Delay:          $DELAY seconds
Preempt:        $PREEMPT
Disable LED:    $NOLED
Disable Button: $NOBUTTON
Brightness:     $BRIGHTNESS

To change these options, run:
$USAGE

Or edit: $SERVICE_PATH


EOF

read -r -d '' UNIT_FILE << EOF
[Unit]
Description=Fan Shim Service
After=multi-user.target

[Service]
Type=simple
WorkingDirectory=$(pwd)
ExecStart=$PYTHON $(pwd)/automatic.py --on-threshold $ON_THRESHOLD --off-threshold $OFF_THRESHOLD --delay $DELAY --brightness $BRIGHTNESS $EXTRA_ARGS
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

printf "Checking for rpi.gpio>=0.7.0 (for Pi 4 support)\n"
$PYTHON - <<EOF
import RPi.GPIO as GPIO
from pkg_resources import parse_version
import sys
if parse_version(GPIO.VERSION) < parse_version('0.7.0'):
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
	printf "Installing rpi.gpio\n"
	$PIP install --upgrade "rpi.gpio>=0.7.0"
else
	printf "rpi.gpio >= 0.7.0 already installed\n"
fi

printf "Checking for Fan SHIM\n"
$PYTHON - > /dev/null 2>&1 <<EOF
import fanshim
EOF

if [ $? -ne 0 ]; then
	printf "Installing Fan SHIM\n"
	$PIP install fanshim
else
	printf "Fan SHIM already installed\n"
fi

printf "Checking for psutil\n"
$PYTHON - > /dev/null 2>&1 <<EOF
import psutil
EOF

if [ $? -ne 0 ]; then
	printf "Installing psutil\n"
	$PIP install psutil fanshim
else
	printf "psutil already installed\n"
fi

printf "\nInstalling service to: $SERVICE_PATH\n"
echo "$UNIT_FILE" > $SERVICE_PATH
systemctl daemon-reload
systemctl enable --no-pager pimoroni-fanshim.service
systemctl restart --no-pager pimoroni-fanshim.service
systemctl status --no-pager pimoroni-fanshim.service

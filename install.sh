#!/bin/bash

LIBRARY_VERSION=`grep version library/setup.cfg | awk -F" = " '{print $2}'`
LIBRARY_NAME=`grep name library/setup.cfg | awk -F" = " '{print $2}'`
PY2_DEPS=`grep py2deps library/setup.cfg | awk -F" = " '{print $2}'`
PY3_DEPS=`grep py3deps library/setup.cfg | awk -F" = " '{print $2}'`

function apt_pkg_install {
	PACKAGES=()
	for PACKAGE in "$@"; do
		printf "Checking for $PACKAGE\n"
		dpkg -L $PACKAGE > /dev/null 2>&1
		if [ "$?" == "1" ]; then
			PACKAGES+=("$PACKAGE")
		fi
	done
	PACKAGES="${PACKAGES[@]}"
	if ! [ "$PACKAGES" == "" ]; then
		echo "Installing missing packages: $PACKAGES"
		sudo apt update
		sudo apt install -y $PACKAGES
	fi
}

printf "$LIBRARY_NAME $LIBRARY_VERSION Python Library: Installer\n\n"

if [ $(id -u) -ne 0 ]; then
	printf "Script must be run as root. Try 'sudo ./install.sh'\n"
	exit 1
fi

cd library

printf "Installing for Python 2..\n"
apt_pkg_install $PY2_DEPS
python setup.py install

if [ -f "/usr/bin/python3" ]; then
	printf "Installing for Python 3..\n"
	apt_pkg_install $PY3_DEPS
	python3 setup.py install
fi

cd ..

printf "Done!\n"

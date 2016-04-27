#!/usr/bin/env bash

WAITTIME=60
DATE=$(date -u +%s)

# get time of last attack
LASTATK=$(cat /var/cctf/locks/$USER.attack)
OKTIME=$(( LASTATK + 60 ))
SECLEFT=$(( OKTIME - DATE ))

if (( SECLEFT <= 0 ))
then

	# submit an attack to the attack list
	echo "$@" >> /var/cctf/attacks/$USER/attacks
	exit 0

else

	echo "$USER needs to wait $SECLEFT seconds before submitting another attack."
	exit 1

fi

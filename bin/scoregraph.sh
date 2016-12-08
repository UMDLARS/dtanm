#!/bin/bash

FIRST=1
while read LINE
do
	TEAM=$(echo $LINE | awk '{ print $1 }')
	RATIO=$(echo $LINE | awk '{ print $2 }')
	ATTACKS=${RATIO##*/}
	PASSED=${RATIO%%/*}
	if [[ $FIRST == 1 ]]
	then
		echo -n "attacks: "
		for i in $(seq 1 $ATTACKS)
		do
			echo -n "#"
		done
		echo " ($ATTACKS attacks)"
		FIRST=0
	fi
	
	echo -n "  $TEAM: "
	if (( $PASSED > 0 ))
	then
		for i in $(seq 0 $PASSED)
		do
			echo -n "#"
			
		done
	fi
	echo " ($PASSED passed)"

done < <(score)


#!/bin/bash

#  If you have permissions issues, copy this
#+ script into the directory where it will be executed.

# crunchbang uses dash instead of sh,
# so call this script explicity using bash:
#	# bash script.sh .
# NOT like this:
#	# . script.sh .
#	# ./script.sh .
#	

dir=$1
for f in $(ls $dir)
do
	echo checking: $f
	#if [ ${#f} -ge 3 ]
	# Use regex to match filenames
	if [[ "$f" =~ .*zip$ ]]
	then
		echo unzipping: $f
		dot_position=$((${#f} - 4))
		unzip ${f:0:$dot_position}
		# Delay
		#sleep 2
	fi
	echo 
done

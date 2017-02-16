#!/bin/bash

dir=/home/user/raid/
device=/dev/sdb1

service mysql stop
umount $device
hdparm -y $device


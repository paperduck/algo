#!/bin/bash

dt="$(date +%Y-%m-%d)"

# use --no-data option to omit data.

filename_algo="db_backup_algo_${dt}.mysql"
printf -- "--\n-- ${dt}\n" > $filename_algo
echo "\nPlease enter root database password:"
mysqldump --comments -uroot -p algo >> $filename_algo

filename_algo_private="db_backup_algo_private_${dt}.mysql"
printf -- "--\n-- ${dt}\n" > $filename_algo_private
echo "\nPlease enter root database password:"
mysqldump --comments -uroot -p algo_private >> $filename_algo_private



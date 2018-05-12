#!/bin/bash

filename="db_backup.mysql"

printf -- "--\n-- $(date)\n" > $filename
printf -- "-- This is a backup of the algo database only.\n--\n\n" >> $filename
echo "\nPlease enter root database password:"
# use --no-data option to omit data.
mysqldump --comments -uroot -p algo >> $filename



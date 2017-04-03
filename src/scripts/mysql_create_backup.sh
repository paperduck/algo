#!/bin/bash

filename="db_backup.mysql"

printf -- "--\n-- $(date)\n--\n\n" > $filename
printf -- "--\n-- This is a backup of the algo database only.\n--\n\n" > $filename
echo "\nPlease enter root database password:"
mysqldump -uroot -p algo >> $filename



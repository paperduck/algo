#!/bin/bash

filename="db_backup.mysql"

printf -- "--\n-- $(date)\n--\n\n" > $filename
echo "\nPlease enter root database password:"
mysqldump -uroot -p algo >> $filename



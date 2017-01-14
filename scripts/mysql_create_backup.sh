#!/usr/bin/bash

filename="mysql_backup.mysql"

printf -- "--\n-- $(date)\n--\n\n" > $filename
mysqldump --all-databases -uroot -p >> $filename



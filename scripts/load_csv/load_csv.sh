#!/usr/bin/bash

# Verify arguments
if [[ "$#" -lt 4 ]]; then
    printf "%s\n" "too few arg(s) to $0" \
    "Usage: bash $0 <db user> <db pw> </path/file> <table name>"
    exit 1
fi

u=$1
pw=$2
f=$3
tn=$4

# Times are stored as UTC by default - server timezone affects value
mysql -u$u -p$pw -e "LOAD DATA INFILE '${f}' \
    INTO TABLE ${tn} \
    FIELDS TERMINATED BY ',' \
    ENCLOSED BY '' \
    LINES TERMINATED BY '\r\n' \
    IGNORE 1 LINES \
    ( @old_date, @old_time, open, high, low, close, volume ) \
    SET date = (SELECT algo_fun_fix_date(@old_date)), \
    time = (SELECT algo_fun_fix_time(@old_time))
    ;" algo


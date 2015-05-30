#!/usr/bin/bash

# Convert date string from MM/DD/YYYY to YYYY-MM-DD
fix_date(){
    old_date=$1
    new_date=$old_date
    echo "$new_date"
}

# Verify arguments
if [[ "$#" -lt 4 ]]; then
    printf "%s\n" "too few arg(s)" \
    "Usage: bash algo_proc_load_csv.sh <db user> <db pw> </path/file> <table name>"
    exit 1
fi

u=$1
pw=$2
f=$3
tn=$4

echo user: $u
echo pw: $pw

mysql -u$u -p$pw -e "SELECT test();" algo

# Times stored as UTC by default - server timezone affects value
mysql -u$u -p$pw -e "LOAD DATA INFILE '$f' \
    INTO TABLE $tn \
    FIELDS TERMINATED BY ',' \
    ENCLOSED BY '' \
    LINES TERMINATED BY '\r\n' \
    IGNORE 1100000 LINES \
    ( @old_date, @old_time, open, high, low, close, volume ) \
    SET date = (SELECT algo_fun_fix_date(@old_date)), \
    time = (SELECT algo_fun_fix_time(@old_time))
    ;" algo


#!/usr/bin/bash

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

# Might need to convert date from MM/DD/YYYY to YYYY-MM-DD
# Times stored as UTC by default - server timezone affects value
# 
mysql -u$u -p$pw -e "LOAD DATA INFILE '$f' \
    INTO TABLE $tn \
    FIELDS TERMINATED BY ',' \
    ENCLOSED BY '' \
    LINES TERMINATED BY '\r\n' \
    IGNORE 1 LINES \
    ( date, time, open, high, low, close, volume ) \
    ;" algo


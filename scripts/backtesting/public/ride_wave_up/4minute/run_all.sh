#!/usr/bin/bash
 
# validate input arguments
if [[ $# -ne 6 ]]; then
    printf "%s\n" "bash $0 <un> <pw> <no.trades> <commish> <principal> <stop amt>"
    exit 1
fi

bash algo_proc_ride_wave_up.sh $1 $2 stock_googl
mysql -u$1 -p$2 -N algo -e "CALL ride_wave_up( '2004-01-01', '09:00:00', ${3}, ${4}, ${5}, ${6} );" > out

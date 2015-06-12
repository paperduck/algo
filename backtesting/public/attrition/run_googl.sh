#!/usr/bin/bash
 
# validate input arguments
if [[ $# -ne 6 ]]; then
    printf "%s\n" "bash $0 <un> <pw> <no.trades> <commish> <principal> <stop amt>"
    exit 1
fi

bash algo_proc_core.sh $1 $2 stock_googl
mysql -u$1 -p$2 -N algo -e "CALL attrition_core( '2010-03-27', '09:15:00', ${3}, ${4}, ${5}, ${6} );" > out

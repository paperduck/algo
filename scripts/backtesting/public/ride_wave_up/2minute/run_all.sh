#!/usr/bin/bash
 
# validate input arguments
if [[ $# -ne 7 ]]; then
    printf "%s\n" "bash $0 <un> <pw> <no.trades> <commish> <tax 0.75> <principal> <stop amt> "
    exit 1
fi

for sym in googl zts xnga nok fb
do
    id=1
    bash algo_proc_backtest.sh $1 $2 stock_${sym}
    # loop through open-->low thresholds
    for o_to_l in 0.01 0.02 0.03 0.05 0.1 0.15 0.2 0.3 0.4 0.5 0.75 1
    do
        # loop through open-->close thresholds
        for o_to_c in 0 -0.5 -0.4 -0.3 -0.2 -0.1 0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9
        do
            mysql -u$1 -p$2 -N algo -e "CALL backtest( '1990-01-01', ${3}, ${4}, ${5}, ${6}, ${7}, ${o_to_l}, ${o_to_c} );" > out_${sym}_${id}
            let "id += 1"
            echo $o_to_l
        done
    done
done



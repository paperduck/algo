#!/usr/bin/bash

# results1:
#  bash run_all.sh user poll 100 1 0.75 3000 0.1

# results2:
#  bash run_all.sh user poll 100 1 0.75 3000 0.01

 
# validate input arguments
if [[ $# -ne 7 ]]; then
    printf "%s\n" "bash $0 <un> <pw> <days> <commish> <tax 0.75> <principal> <stop amt> "
    exit 1
fi

for sym in googl #zts xnga nok fb
do
    id=1
    bash algo_proc_backtest.sh $1 $2 stock_${sym}

    # loop through high-->close thresholds (e.g. high - close < 0.1)
    for h_to_c in 0 0.02 0.04 0.06 0.08 
    do
        # loop through open-->low thresholds
        for o_to_l in 0.02 0.04 0.1 0.2 0.4 0.7 1
        do
            # loop through open-->close thresholds
            for o_to_c in '-0.4' '-0.2' '0' '0.2' '0.4' '0.6' '0.8' 
            do
                mysql -u$1 -p$2 -N algo -e "CALL backtest( '1990-01-01', ${3}, ${4}, ${5}, ${6}, ${7}, ${o_to_l}, ${o_to_c}, ${h_to_c} );" > out_${sym}_${id}
                echo ----------------------
                echo out_${sym}_${id}
                echo open to low: $o_to_l
                echo open to close: $o_to_c
                echo high to close: $h_to_c
                let "id += 1"
            done
        done
    done
done



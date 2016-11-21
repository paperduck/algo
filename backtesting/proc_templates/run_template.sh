#!/usr/bin/bash

# validate input arguments
if [[ $# -ne 7 ]]; then
    printf "%s\n" "bash $0 <un> <pw> <days> <commish> <tax 0.75> <principal> <stop amt> "
    exit 1
fi

outfile="out/out_all"
echo > $outfile

for sym in goog fb
do
    id=1
    bash proc_template.sh $1 $2 stock_${sym}

    # loop through high-->close thresholds (e.g. high - close < 0.1)
    for h_to_c in 1 2 3
    do
        # loop through open-->low thresholds
        for o_to_l in 1 2 3
        do
            # loop through open-->close thresholds
            for o_to_c in 1 2 3
            do
                echo ---------------------- >> $outfile
                echo out_${sym}_${id} >> $outfile
                echo open to low: $o_to_l >> $outfile
                echo open to close: $o_to_c >> $outfile
                echo high to close: $h_to_c >> $outfile
                mysql -u$1 -p$2 -N algo -e "CALL backtest( '1990-01-01', ${3}, ${4}, ${5}, ${6}, ${7}, ${o_to_l}, ${o_to_c}, ${h_to_c} );" > out/out_${sym}_${id}
                let "id += 1"
            done
        done
    done
done



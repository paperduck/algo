#!/usr/bin/bash

#############################################################
#############################################################
# To view output in progress:
#   $ watch 'cat out/out_all'
# 
# Sample script to run:
#   $ bash run_proc.sh user poll 1000 1 0.75 10000 0.005
#############################################################
#############################################################

# validate input arguments
if [[ $# -ne 6 ]]; then
    printf "%s\n" "bash $0 <un> <pw> <days> <commish> <tax 0.75> <principal>"
    exit 1
fi

db_un=$1
db_pw=$2
days=$3
commish=$4
tax=$5
princ=$6

outfile="out/out_all"
echo > $outfile

# iterate through symbols
#
# akam (akamai tech.) fell a lot in its initial year (1999-00).
# googl has risen steadily except fell during 2013
for sym in ge akam googl
do
    id=1
    bash create_proc.sh $db_un $db_pw stock_${sym}

    # iterate through 'in_num_pre_swing_bars_needed'
    for min_bars in 2 3 4 5 6 7 8 9 10
    do
        # iterate through 'in_min_pre_swing_drawdown_percent' (percent as decimal)
        for min_pct_drop in 0.001 0.005 .01
        do
            # iterate through 'in_min_upswing_percent' (percent as decimal)
            for min_up_pct in 0.001 0.05 0.01 0.02 0.03
            do
                # iterate through trailing stop % (% as decimal)
                for ts_pct in 0.006 0.008 0.01 0.02
                do
                    echo ---------------------- >> $outfile
                    echo out_${sym}_${id} >> $outfile               # filename of this output file
                    echo min bars in drop: $min_bars >> $outfile    # parameter
                    echo min % drop: $min_pct_drop >> $outfile      # parameter
                    echo min upswing %: $min_up_pct >> $outfile     # parameter
                    echo tr. stop %: $ts_pct >> $outfile            # parameter
                    mysql -u${db_un} -p${db_pw} -N algo -e "CALL backtest( '1990-01-01', ${days}, ${commish}, ${tax}, \
                        ${princ}, ${ts_pct}, ${min_bars}, ${min_pct_drop}, ${min_up_pct} );" > out/out_${sym}_${id}
                    let "id += 1"
                done
            done
        done
    done
done



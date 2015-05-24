# INPUT PARAMETERS
# 	dir_path
# 		Directory that contains the CSV files.
#	tn_pre
#		Table name prefix. 	
# REMARKS
#	Note that the CSV files from pi trading have the a 
#	'.txt' extension.
# EXAMPLES
#	#> load_csv dji_ mydir/

#!/bin/bash
if [ -z "$1" ]; then
    echo 'missing directory path'
    exit 1
fi
dir_path=$1
if [ -z "$2" ]; then
    echo 'missing table name prefix'
    exit 1
fi
tn_pre=$2
tn=''
echo table name prefix: $tn_pre
echo directory: $dir_path
for f in $( ls ${dir_path} );
do
    if [[ $f =~ [tT][xX][tT] ]] ; then
        echo file: $f
        # derive table name
        # Extract everything from file name up to extension
        # transform uppercase to lowercase
        tn=$( echo ${f%.txt} | tr [:upper:] [:lower:] ) # case sensitive
        tn=${tn_pre}_${tn}
        echo loading file $f into table $tn
        # put data into database
    #	echo ${mysql < call_algo_proc_test.mysql}
        #mysql < algo_proc_load_pitrading_stocks ($dir/$f, $tn)
    fi
done

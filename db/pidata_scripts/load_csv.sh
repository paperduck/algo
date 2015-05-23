# INPUT PARAMETERS
# 	d
# 		Directory that contains the CSV files.
#	tn_pre
#		Table name prefix. 	
# REMARKS
#	Note that the CSV files from pi trading have the a 
#	'.txt' extension.
# EXAMPLES
#	#> load_csv dji_ mydir/

#!/bin/bash
tn_pre=$1
dir=$2
tn=""
echo table name prefix: $tn_pre
echo directory: $dir
for f in $( ls ${dir}/*.txt );
do
	# derive table name
	# Extract everything from file name up to extension
	# convert to lowecase
	#tn = ${f%.txt} | tr [:upper:] [:lower:]

	#tn=$( echo "${tn}" | tr [:upper:] [:lower:] ) # this syntax works

	tn=$( echo ${f%.txt} | tr [:upper:] [:lower:] )
	tn = "$tn_pre"_"$tn"
	echo loading file $f into table $tn
	# put data into database
	echo ${mysql < call_algo_proc_test.mysql}
	#mysql < algo_proc_load_pitrading_stocks ($dir/$f, $tn)
done

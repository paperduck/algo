# Input Parameters:
#
# 	d
# 		Directory that contains the data. Data could be in text files, csv, etc.
# Remarks:
#

#!/bin/bash
dir=$1
tn=""
echo directory: $dir
for f in $( ls $dir );
do
	# unzip if needed
	dot_index = 

	if [ #
	# derive table name from file name (conver to lowecase)
	tn=${f%%.txt}

	echo loading $tn
	# put data into database
	echo ${mysql < call_algo_proc_test.mysql}
	#mysql < algo_proc_load_pitrading_stocks ($dir/$f, $tn)
done

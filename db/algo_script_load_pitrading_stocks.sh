

# Input Parameters:
#
# 	directory path
# 		Directory that contains the data. Data could be in text files, csv, etc.
#
#	Filename filter
#		Specify wildcards/regex of files to look for and load into database.
#
# Remarks
#	Destination table will be named same as file, minus the filename's extension, if any.

#!/bin/bash

dir="priv_historical_data/pitrading/stocks_dvd/sp500/"
for f in $( ls $dir );
do
	mysql algo_proc_load_pitrading_stocks.mysql $dir
	# mysql  algo_proc_load_pitrading_stocks.mysql <filename_minus_extension>
done

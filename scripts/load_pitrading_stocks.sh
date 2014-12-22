

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



for each file in directory that matches filter:
	mysql  algo_script_load_pitrading_stock.mysql <filename_minus_extension>


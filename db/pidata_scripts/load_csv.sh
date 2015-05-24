# INPUT PARAMETERS
# 	dir_name    Name of directory that contains the CSV files.
#	tn_pre      Table name prefix.
#   db_user     Database username
#   db_pass     Database password 	
# REMARKS
#	Note that the CSV files from pi trading have the a 
#	'.txt' extension.
# EXAMPLES
#	#> load_csv dji_ mydir/

#!/bin/bash

# Verify arguments
if [ -z "$1" ]; then
    echo 'missing directory path'
    exit 1
fi
dir_name=$1
if [ -z "$2" ]; then
    echo 'missing table name prefix'
    exit 1
fi
tn_pre=$2
if [ -z "$3" ]; then
    echo 'missing database username'
    exit 1
fi
db_user=$3
if [ -z "$4" ]; then
    echo 'missing database password'
    exit 1
fi
db_pass=$4

pwd=$(pwd)
tn=''
full_file_path=''
echo table name prefix: $tn_pre
echo directory: $dir_name
for f in $( ls ${dir_name} );
do
    if [[ $f =~ \.txt$ ]] ; then
        echo file: $f
        # derive table name
        # Extract everything from file name up to extension
        # transform uppercase to lowercase
        tn=$( echo ${f%.txt} | tr [:upper:] [:lower:] ) # case sensitive
        tn=${tn_pre}_${tn}
        full_file_path="${pwd}/${dir_name}/$f"
        echo loading file $full_file_path into table $tn
        # Call MySQL batch script to load CSV data into table
        echo $(mysql -u${db_user} -p${db_pass} < call_test.mysql)
        #mysql < algo_proc_load_pitrading_stocks ($dir/$f, $tn)
        echo
    fi
done
echo
echo done

#!/usr/bin/bash

###########################################################
# INPUT PARAMETERS
#   - Database username
#   - Database password 	
# 	- Full path of directory that contains the CSV files,
#       including final slash.
#	- Table name prefix.
# REMARKS
#	Note that the CSV files from pi trading have the a 
#	'.txt' extension.
# EXAMPLES
#
###########################################################
# Various ways to pass arguments to proc from command line:
#
#   $ mysql --user=your_username --execute="call stored_procedure_name()" db_name
#   
#   $ mysql -u your_username --password=your_password db_name <<!!
#   call stored_procedure_name();
#   !!

# Verify arguments
if [[ "$#" -lt 4 ]]; then
    printf "%s\n" "missing arg(s)" \
    "Usage: bash call.sh <db user> <db pw> <dir> <tn prefix>"
    exit 1
fi

db_user=$1
db_pass=$2
dir=$3
tn_pre=$4

pwd=$(pwd)
tn=''
full_file_path=''
cmd=''
echo table name prefix: $tn_pre
echo directory: $dir
echo

# Prepare procedure: algo_proc_drop_table
echo Creating algo_proc_drop_table ...
mysql -u$1 -p$2 algo < algo_proc_drop_table.mysql
# Prepare procedure: algo_proc_create_table
echo Creating proc algo_proc_create_table_stock ...
mysql -u$1 -p$2 algo < algo_proc_create_table_stock.mysql
# Prepare procedure: algo_proc_load_csv
echo Creating proc algo_proc_load_csv ...
mysql -u$1 -p$2 algo < algo_proc_load_csv.mysql
# Prepare function: algo_fun_fix_date
echo Creating function algo_fun_fix_date ...
mysql -u$1 -p$2 algo < algo_fun_fix_date.mysql
# Prepare function: algo_fun_fix_time
echo Creating function algo_fun_fix_time ...
mysql -u$1 -p$2 algo < algo_fun_fix_time.mysql

for f in $( ls ${dir} );
do
    # Do for each file with '.txt' extension
    if [[ $f =~ \.txt$ ]] ; then
        # derive table name from filename
        # Extract everything from file name up to extension
        # transform uppercase to lowercase
        tn=$( echo ${f%.txt} | tr [:upper:] [:lower:] ) # case sensitive
        tn=${tn_pre}_${tn}
        full_file_path="${dir}${f}"
        
        echo ----------------------------------------------
        echo loading file
        echo "    $full_file_path"
        echo into table
        echo "    $tn"
        echo Dropping table...
        mysql -u$db_user -p$db_pass -e "CALL algo_proc_drop_table('${tn}');" algo
        echo Creating table...
        mysql -u$db_user -p$db_pass -e "CALL algo_proc_create_table_stock('${tn}');" algo
        echo Loading CSV file...
        bash load_csv.sh $db_user $db_pass $full_file_path $tn
        echo
    fi
done
echo done
echo

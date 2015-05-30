#!/usr/bin/bash

###########################################################
# INPUT PARAMETERS
#   - Database username
#   - Database password 	
# 	- Name of directory that contains the CSV files.
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



proc_drop_table(){
    echo proc_drop_table
    mysql -u$1 -p$2 algo < algo_proc_drop_table_stock.mysql
}
run_drop_table(){
    echo run_drop_table
    mysql -u$1 -p$2 -e "CALL algo_proc_drop_table_stock('${3}');" algo
}
proc_create_table(){
    echo proc_create_table
    mysql -u$1 -p$2 algo < algo_proc_create_table_stock.mysql
}
run_create_table(){
    echo run_create_table
    mysql -u$1 -p$2 -e "CALL algo_proc_create_table_stock('${3}');" algo
}
proc_load_csv(){
    echo proc_load_csv
        
}
run_load_csv(){
    echo run_load_csv
}

# Verify arguments
if [[ "$#" -lt 4 ]]; then
    printf "%s\n" "missing arg(s)" \
    "Usage: bash call.sh <db user> <db pw> <dir> <tn prefix>"
    exit 1
fi

db_user=$1
db_pass=$2
dir_name=$3
tn_pre=$4

pwd=$(pwd)
tn=''
full_file_path=''
cmd=''
echo table name prefix: $tn_pre
echo directory: $dir_name
echo

proc_drop_table $db_user $db_pass
proc_create_table $db_user $db_pass
proc_load_csv $db_user $db_pass

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
        run_drop_table $db_user $db_pass $tn
        run_create_table $db_user $db_pass $tn
        run_load_csv $db_user $db_pass $f $tn
        echo
    fi
done
echo done
echo

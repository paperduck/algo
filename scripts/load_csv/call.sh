###########################################################
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

###########################################################
# Various ways to pass arguments to proc from command line:
#
#   $ mysql --user=your_username --execute="call stored_procedure_name()" db_name
#   
#   $ mysql -u your_username --password=your_password db_name <<!!
#   call stored_procedure_name();
#   !!


#!/bin/bash

proc_drop_table(){
    echo proc_drop_table
}
run_drop_table(){
    echo run_drop_table
}
proc_create_table(){
    echo proc_create_table
}
run_create_table(){
    echo run_create_table
    #cmd='mysql -u '${db_user}' -p '${db_pass}' algo -e "CALL algo_proc_create_table_stock('\'${tn}\'')"'
}
proc_load_csv(){
    echo proc_load_csv
}
run_load_csv(){
    echo run_load_csv
    #cmd='mysql -u '${db_user}' -p '${db_pass}' algo --execute="CALL algo_proc_load_csv('\'${full_file_path}\'', '\'${tn}\'');"'
}
run_mysql(){
    echo mysql
}

# Verify arguments
if [[ "$#" -lt 4 ]]; then
    printf "%s\n" "missing arg(s)" \
    "Usage: bash call.sh <dir> <tn prefix> <db user> <db pw>"
    exit 1
fi

dir_name=$1
tn_pre=$2
db_user=$3

db_pass=$4

pwd=$(pwd)
tn=''
full_file_path=''
cmd=''
echo table name prefix: $tn_pre
echo directory: $dir_name
echo

proc_drop_table
proc_create_table
proc_load_csv

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

        run_drop_table $tn
        run_create_table $tn
        run_load_csv $f $tn

        echo
    fi
done
echo done
echo

#############################################
# Synopsis:
#   Test passing arguments into function/proc
#   from command line

#!/usr/bin/bash

if [[ "$#" -lt 3 ]]; then
    #echo 'missing arg(s)'
    printf "%s\n" "ERROR: Missing arg(s)." \
        "Usage: bash call.sh <username> <pw> <arg>"
    exit 1
fi
user=$1
pw=$2
arg=$3

cmd='mysql -u'${user}' -p'${pw}' algo --execute="SELECT algo.test('${arg}');"'
eval $cmd
echo

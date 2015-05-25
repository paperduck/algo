#############################################
# Synopsis:
#   Test passing arguments into function/proc
#   from command line

#!/usr/bin/bash

if [ -z $1 ]; then
    echo missing arg
    exit 1
fi
arg=$1
cmd="mysql -uuser -ppoll algo --execute=\"SELECT algo.test();\""
echo
echo $cmd
echo
command $cmd


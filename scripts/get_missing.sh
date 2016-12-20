
# download files that haven't been downloaded yet.
# Match on files only (not size, contents, etc.)

# read file that has list of urls
for url in $(cat -s urls.txt)
do
    # See if I have that file yet.
    # I might have already decompressed the file, so
    # ignore .gz and .tar extensions.
    get=1
    for file in $(ls -1)
    do
        base=$file
        # trim .gz
        if [ "${base: -3}" = ".gz" ]
        then
            base=${base::-3}
        fi
        # trim .tar
        if [ "${base: -4}" = ".tar" ]
        then
            base=${base::-4}
        fi
        # if (url - base filename) is different than  (url), then I have the file
        if [ "${url/$base}" != $url ]
        then
            get=0
            #echo "don't get:  " $url
            break
        fi
    done
    if [ $get -eq 1 ]; then
        wget -nc $url
    fi
done 



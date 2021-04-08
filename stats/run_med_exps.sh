path=$(pwd)
IFS_save=$IFS
for d in */ ; do
    cd $path
    for e in $d*; do
        cd $e
        cp ../../../median.py ./
        IFS='/'
        read -a split <<< "$e"
        python median.py -f ${split[1]}
        IFS=$IFS_save
        cd ../../
    done
done
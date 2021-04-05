path=$(pwd)
IFS_save=$IFS
for d in */ ; do
    cd $path
    for e in $d*; do
        cd $e
        cp ../../../averagator.py ./averagator.py
        IFS='/'
        read -a split <<< "$e"
        python averagator.py -f ${split[1]}
        IFS=$IFS_save
        cd ../../
    done
done
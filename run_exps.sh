#!/bin/bash


current_TA="AITA"
mode=""
# Exp number
for e in {1..3}; do
    mode=""
    if [[ $e -eq 1 ]]; then
        mode="æ"
    elif [[ $e -eq 2 ]]; then
        mode="@"
    fi

    # Number of robot
    for r in `seq 10 10 50`; do
        # Run number
        for i in {1..5}; do 
            if [[ $e -eq 3 ]]; then
                for m in @ £ ; do
                    python simulation.py -p 2000 -r $r -s False -b False -t False -a True -n 0.3 -f "03${current_TA}/EXP${e}/${m}${current_TA}_r${r}/RUN${i}.csv" -e $e
                done
            else
                python simulation.py -p 2000 -r $r -s False -b False -t False -a True -n 0.3 -f "03${current_TA}/EXP${e}/${mode}${current_TA}_r${r}/RUN${i}.csv"  -e $e
            fi
        done
    done
done
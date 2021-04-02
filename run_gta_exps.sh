current_TA="GTA"
mode=""
# Exp number
for e in {1..3}; do
    mode=""
    if [[ $e -eq 1 ]]; then
        mode="æ"
    elif [[ $e -eq 2 ]]; then
        mode="@"
    fi

    
    # Run number
    for i in {1..5}; do 
        if [[ $e -eq 3 ]]; then
            for m in @ £ ; do
                python simulation.py -p 2000 -r 40 -s False -b False -t False -a True -n 0.01 -f "${current_TA}/EXP${e}/${m}${current_TA}_r40/RUN${i}.csv" -e $e
            done
        else
            python simulation.py -p 2000 -r 40 -s False -b False -t False -a True -n 0.01 -f "${current_TA}/EXP${e}/${mode}${current_TA}_r40/RUN${i}.csv"  -e $e
        fi
    done
    
done
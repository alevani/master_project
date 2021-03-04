#!/bin/bash
# Lazy me wants to run this on a weekend a do nothing

for e in {1..2}; do
    for i in {1..5}; do
        for r in `seq 10 10 50`; do
            python simulation.py -r $r -p 2000 -s False -b False -t False -a False -f EXP/ALONE/EXP$e/RUN$i/stats25_ATAI_EXP1_R$r.csv -e $e
        done
    done
done
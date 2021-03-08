#!/bin/bash
# Lazy me wants to run this on a weekend a do nothing

for e in {1..3}; do
    for i in {1..5}; do
        # for r in `seq 10 10 50`; do
        python simulation.py -p _RUN272000 -s False -b False -t False -a False -f EXP/ALONE/EXP$e/stats25_ATAI_EXP1_R27_RUN$i.csv -e $e
            # python simulation.py -p 2000_RUNr  -s False -b False -t False -a False -f EXP/ALONE/EXP$e/stats25_ATAI_EXP1_R$r_RUN$i.csv -e $e
        # done
    done
done
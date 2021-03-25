#!/bin/bash
for i in {1..5}; do 
    python simulation.py -p 2000 -r 40 -s False -b False -t False -a True -n 0.00 -f "runs/@run${i}" -e 1
done
#!/bin/bash

for i in {1..5}; do 
#! Before running the following experiment, turn the directional communication on
python simulation.py -p 2000 -r 40 -s False -b False -t False -a True -n 0.3 -f "FAITA/EXPSA/£FAITA_r40/RUN${i}.csv" -e 1
done

for i in {1..5}; do 
#! Before running the following experiment, change the comm range
python simulation.py -p 2000 -r 40 -s False -b False -t False -a True -n 0.3 -f "FAITA/EXPSB15/£FAITA_r40/RUN${i}.csv" -e 1
done

for i in {1..5}; do 
#! Before running the following experiment, change the comm range
python simulation.py -p 2000 -r 40 -s False -b False -t False -a True -n 0.3 -f "FAITA/EXPSB30/£FAITA_r40/RUN${i}.csv" -e 1
done

for i in {1..5}; do 
#! Before running the following experiment, change the comm range
python simulation.py -p 2000 -r 40 -s False -b False -t False -a True -n 0.3 -f "FAITA/EXPSB50/£FAITA_r40/RUN${i}.csv" -e 1
done

for i in {1..5}; do 
#! Before running the following experiment, change the comm range
python simulation.py -p 2000 -r 40 -s False -b False -t False -a True -n 0.3 -f "FAITA/EXPSB100/£FAITA_r40/RUN${i}.csv" -e 1
done
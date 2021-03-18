#!/bin/bash

set -o errexit
set -o nounset

g++ -Iexample/ini/ -Iexample/ -o example/program_ini.out \
  example/program_ini.cpp example/ini/Parameters.cpp example/ini/ini.cpp -lm

python3 parameter_optimizer.py \
    --optimization-choice=minimum \
    --parameter-passing=ini \
    --program-command=example/program_ini.out \
    --parameter-file=example/optimization_ini.ini \
    --result-file=result.txt \
    --calculation-cache-file=optimization_results.csv \
    --parameter=optimization_phi:10:25 \
    --parameter=optimization_v0:10:200 \

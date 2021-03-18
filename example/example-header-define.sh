#!/bin/bash

python3 parameter_optimizer.py \
    --optimization-choice=minimum \
    --parameter-passing=header-define \
    --program-command=example/program_header.sh \
    --parameter-file=example/optimization_header.h \
    --result-file=result.txt \
    --calculation-cache-file=optimization_results.csv \
    --parameter=optimization_phi:10:25 \
    --parameter=optimization_v0:10:200 \

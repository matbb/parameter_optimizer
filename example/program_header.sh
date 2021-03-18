#!/bin/bash

set -o errexit
set -o nounset

g++ -Iexample/ini/ -Iexample/ -o example/program_header.out example/program_header.cpp -lm
example/program_header.out

#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

P=$DIR
cd ..
P=$PYTHONPATH:$PWD
cd $DIR

echo $P

PYTHONPATH=$P python -m unittest discover -s suites $@
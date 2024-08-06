#!/bin/bash
echo "GRLRR STARTING"

# get in the project
cd Documents/Projects/grlrr/

# activate enviroment
source .venv/bin/activate

#store the proces id:
echo 'Process ID: ' >>grlrr.log
echo $$ >>grlrr.log

# start the main program
python main.py
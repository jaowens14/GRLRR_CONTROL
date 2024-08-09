#!/bin/bash
echo "GRLRR Starting" >> grlrr.log

# debugging command
# strace -e trace=kill -o >(cat >> ./Documents/Projects/grlrr/grlrr.log) ./Documents/Projects/grlrr/grlrr_run.sh
# get in the project
cd Documents/Projects/grlrr/ 

# activate enviroment
source .venv/bin/activate

# set up the ap
echo "Setting up Access Point: " >> grlrr.log
nmcli device wifi hotspot ssid grlrr2024 password grlrr2024 ifname wlan0 >> grlrr.log

# store the creditials
nmcli dev wifi show-password >> grlrr.log

# start the main program
python main.py

echo "GRLRR Running" >> grlrr.log
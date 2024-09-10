#!/bin/bash
echo "GRLRR Starting"

# debugging command
# strace -e trace=kill -o >(cat >> ./Documents/Projects/grlrr/grlrr.log) ./Documents/Projects/grlrr/grlrr_run.sh


# set up the ap
#echo "Setting up Access Point: "
#nmcli device wifi hotspot ssid grlrr2024 password grlrr2024 ifname wlan0

# store the creditials
# nmcli dev wifi show-password

# get in the project
cd Documents/Projects/GRLRR_CONTROL/ 

# activate enviroment
source .venv/bin/activate

# start the main program
echo "GRLRR Running"
python main.py



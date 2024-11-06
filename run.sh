
source .venv/bin/activate

connection_name=$(nmcli -g name connection show | head -1)

if [[ "$connection_name" == "Hotspot" ]]; then
    echo "Hotspot already enabled"
else
    nmcli dev wifi hotspot ifname wlan0 ssid grlrr2024 password grlrr2024

fi

echo "Starting..."
python main.py
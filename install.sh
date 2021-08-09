sudo apt-get update -yy
sudo apt install python3 python3-pip python3-venv
sleep 2
python3 -m venv ../BotsideP2P
sleep 2
source bin/activate
#pip3 -r requirements.txt
pip3 install python3-xlib requests kademlia

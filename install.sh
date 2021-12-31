sudo apt-get -yy update 
sudo apt -y install python3 python3-pip python3-venv
sleep 2
python3 -m venv ../BotsideP2P
sleep 2
export DIR=`pwd`
source $DIR/bin/activate && pip3 install requests kademlia
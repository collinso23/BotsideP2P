sudo apt-get -yy update 
sudo apt -y install python3 python3-pip python3-venv
PROJECT_HOME=$(find `pwd`  -name BotsideP2P 2>/dev/null)
cd $PROJECT_HOME
export DIR=`pwd`
python3 -m venv $PROJECT_HOME/
source $PROJECT_HOME/bin/activate && pip3 install -r requirements.txt
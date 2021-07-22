BOOTSTRAPPER=192.168.50.131
PORT=8468

if [[ ! $# -eq 2 ]]; then
read -p "Enter a KEY" KEY

read -p "Enter a UUID" UUID
fi

python connect.py $BOOTSTRAPPER $PORT $KEY $UUID
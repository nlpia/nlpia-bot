if [ -z "$1" ] ;
then
  interval=60
else
  interval=$1
fi

while true ;
do
  echo $(date) >> nvidia-smi.log ;
  echo $(date) ;
  nvidia-smi | egrep "[0-9]+%" >> nvidia-smi.log || echo "Unable to allocate memory with nvidia-smi" >> nvidia-smi.log ;
  sleep 2;
  nvidia-smi | egrep "[0-9]+%" || echo "Unable to allocate memory with nvidia-smi" ;
  sleep $interval ;
done

#/bin/sh 

date=$(date '+%d_%m_%Y%H:%M:%S')
#buildnum=`git log --pretty=format:'%h' -n 1`
echo "num = \""$date"\"" > ./src/buildnum.py
echo "Build number generated: "$date

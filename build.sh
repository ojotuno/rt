#/bin/sh 

buildnum=`git log --pretty=format:'%h' -n 1`
echo "num = \""$buildnum"\"" > ./src/buildnum.py
echo "Build number generated: "$buildnum
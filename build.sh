#/bib/bash

buildnum=`git log --pretty=format:'%h' -n 1`
echo "num = \""$buildnum"\"" > ./src/buildnum.py

echo "Installing RT into /usr/local/bin"
sudo mkdir -p /usr/local/src/rt && sudo cp -v ./src/* /usr/local/src/rt/
sudo cp rt /usr/local/bin/
sudo chown root:root /usr/local/bin/rt
sudo chown -R root:root /usr/local/src/rt
sudo chmod 555 /usr/local/bin/rt
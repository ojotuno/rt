#/bin/sh 

FILE=build.sh
if [ -f "$FILE" ]; then
    sh build.sh
else
    echo "Building omited"
fi

echo "Installing RT into /usr/local/bin"
sudo mkdir -p /usr/local/src/rt && sudo cp -v ./src/* /usr/local/src/rt/
sudo cp -v rt /usr/bin/
sudo chown root:root /usr/bin/rt
sudo chown -R root:root /usr/local/src/rt
sudo chmod 555 /usr/local/bin/rt
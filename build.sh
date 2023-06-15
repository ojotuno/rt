#/bib/bash

rm -rf build
rm -rf bin

mkdir build
mkdir bin

#if pyinstaller is not recognised -> run pip install pyinstaller for the pip version wanted
pyinstaller $HOME/dev/rt/src/rt.py --distpath ./bin --workpath ./build --paths $HOME/dev/rt/src  --onefile

echo "Installing RT into /opt/rt ..."
sudo cp -v ./bin/rt /usr/bin



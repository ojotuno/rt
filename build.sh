#/bib/bash

rm -rf build
rm -rf bin

mkdir build
mkdir bin

pyinstaller ./src/rt.py --distpath ./bin --workpath ./build --paths ./src  --onefile
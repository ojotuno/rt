#/bib/bash

rm -rf build
rm -rf bin

mkdir build
mkdir bin

#if pyinstaller is not recognised -> run pip install pyinstaller for the pip version wanted
pyinstaller ./src/rt.py --distpath ./bin --workpath ./build --paths ./src  --onefile

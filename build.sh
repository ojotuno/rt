#!/bin/sh
# Generate the build number shown by `rt --help`.
cd "$(dirname "$0")"
date=$(date '+%d%m%Y-%H%M%S')
echo "num = \"$date\"" > ./src/rt/buildnum.py
echo "Build number generated: $date"

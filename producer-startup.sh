#!/bin/bash

here=$(pwd)/$(dirname "$0")


## install
cd $here/data-crawler/
sh install.sh


## start
cd $here/data-crawler/
nohup sh jvm-start.sh &

cd $here/scripts/
nohup python face-detect.py &

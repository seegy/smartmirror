#!/bin/bash

here=$(pwd)/$(dirname "$0")


## install

cd $here/webserver/
npm install

cd $here/../stuff/data-crawler/
sh install.sh


## start

cd $here/../stuff/data-crawler/
nohup sh jvm-start.sh &

cd $here/../stuff/scripts/
nohup python face-detect.py &

cd $here/webserver/
nohup npm start &
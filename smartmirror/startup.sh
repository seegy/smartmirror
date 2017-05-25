#!/bin/bash

here=$(dirname "$0")

npm install $here/webserver/
npm update $here/webserver/

cd $here/../stuff/data-crawler/
sh jvm-start.sh

cd $here/../stuff/scripts/
nohup python face-detect.py &

cd $here/webserver/
nohup npm start &


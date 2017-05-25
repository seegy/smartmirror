#!/bin/bash

here=$(dirname "$0")

cd $here/../stuff/data-crawler/
nohup sh jvm-start.sh &

cd $here/../stuff/scripts/
python face-detect.py &

cd $here/webserver/
npm install $here/webserver/
nohup npm start &
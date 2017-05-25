#!/bin/bash

here=$(dirname "$0")

npm install $here/webserver/
npm update $here/webserver/

sh $here/../data-crawler/jvm-start.sh
nohup python $here/../scripts/face-detect.py &

cd $here/webserver/
nohup npm start &


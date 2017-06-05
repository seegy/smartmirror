#!/bin/bash

here=$(pwd)/$(dirname "$0")


## install
cd $here/gui-server/
npm install

## start
cd $here/gui-server/
nohup npm start &
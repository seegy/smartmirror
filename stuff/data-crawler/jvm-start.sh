#!/bin/bash

javaArgs="-Xmx20m"
path=$(pwd)

cd  "`dirname \"$0\"`"

lein compile
lein uberjar

nohup java $javaArgs -jar target/data-crawler-0.1.0-SNAPSHOT-standalone.jar &

cd $path
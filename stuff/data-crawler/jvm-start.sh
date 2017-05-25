#!/bin/bash

javaArgs="-Xmx20m"
path=$(pwd)
here=$(dirname "$0")

cd here

lein compile
lein uberjar

cd $path

java $javaArgs -jar $here/target/data-crawler-0.1.0-SNAPSHOT-standalone.jar
#!/bin/bash

javaArgs="-Xmx20m"
here=$(pwd)/$(dirname "$0")

java $javaArgs -jar $here/target/data-crawler-0.1.0-SNAPSHOT-standalone.jar
#!/bin/bash

here=$(pwd)/$(dirname "$0")

cd $here

lein compile
lein uberjar

#!/bin/sh

docker pull redis
docker run -p 6379:6379 --name some-redis -d redis

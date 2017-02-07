#!/usr/bin/env bash

path/to/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic train-news
path/to/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic weather-news
path/to/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic faces

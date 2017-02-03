# my-raspberry-smarthome

This repository works as gathering for number of smarthome applications based on the [RaspberryPie Model 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/) and [Apache Kafka](https://kafka.apache.org/). Every single IOP application, mostly Python scripts, are working as an autonomous cell and delivers its informations to one local Kafka system. Consumers, such as monitors or output applications, get their data basically from Kafka and process them by their own.

A list of applications:

* heat sensors for bbq grills
* "hey, did i close the door?"-sensors
* Smart Mirror
* ...


## Install introductions

On the raspberry:

```
sudo pip install kafka
cd ~
wget http://ftp.fau.de/apache/kafka/0.10.1.1/kafka_2.11-0.10.1.1.tgz
tar -xzf kafka_2.11-0.10.1.1.tgz

echo "/home/pi/kafka_2.11-0.10.1.1/bin/zookeeper-server-start.sh -daemon /home/pi/kafka_2.11-0.10.1.1/config/zookeeper.properties ; /home/pi/kafka_2.11-0.10.1.1/bin/kafka-server-start.sh -daemon /home/pi/kafka_2.11-0.10.1.1/config/server.properties" >> kafka-startup.sh


/home/pi/kafka_2.11-0.10.1.1/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic my-topic

/home/pi/kafka_2.11-0.10.1.1/bin/kafka-topics.sh --list --zookeeper localhost:2181


```

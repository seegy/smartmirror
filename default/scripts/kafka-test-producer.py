#!/usr/bin/env python
import threading, logging, time, ConfigParser

from kafka import KafkaConsumer, KafkaProducer

Config = ConfigParser.ConfigParser()
Config.read('./config.ini')

kafkaHost = Config.get('Kafka', 'host')
kafkaPort = Config.get('Kafka', 'port')
topic = Config.get('test-producer', 'topic')

class Producer(threading.Thread):
    daemon = True

    def run(self):
        producer = KafkaProducer(bootstrap_servers=kafkaHost+':'+kafkaPort)

        while True:
            producer.send(topic, b"test")
            producer.send(topic, b"\xc2Hola, mundo!")
            time.sleep(1)



def main():
    threads = [
        Producer()
    ]

    for t in threads:
        t.start()

    time.sleep(10)

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
        level=logging.INFO
        )
    main()

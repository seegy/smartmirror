#!/usr/bin/python2.7

import sys
from time import sleep, gmtime, strftime
import cv2
import picamera
import os

import threading, logging, time, ConfigParser
from kafka import KafkaProducer

Config = ConfigParser.ConfigParser()
Config.read('./config.ini')

kafkaHost = Config.get('Kafka', 'host')
kafkaPort = Config.get('Kafka', 'port')
topic = Config.get('face-producer', 'topic')



def find_a_face(image):
    face_cascade = cv2.CascadeClassifier('/home/pi/opencv-3.0.0/data/haarcascades/haarcascade_frontalface_default.xml')

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags = cv2.CASCADE_SCALE_IMAGE
    )

    # iterate over all identified faces and try to find eyes
    for (x, y, w, h) in faces:
        return True


if __name__ == "__main__":

    cam = picamera.PiCamera()
    producer = KafkaProducer(bootstrap_servers=kafkaHost+':'+kafkaPort)

    while True:
        image_file = '/tmp/face-detect.jpg'
        cam.capture(image_file)
        image = cv2.imread(image_file)
        if find_a_face(image):
            print( strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ': found a face!')
            producer.send(topic, b'{"found" : true, "person": "any"}')

        os.remove(image_file)
        sleep(0.1)

#!/usr/bin/python2.7

import sys
from time import sleep, gmtime, strftime
import cv2, picamera, os, threading, logging, time, ConfigParser
import numpy as np
from PIL import Image
from kafka import KafkaProducer
import scipy.ndimage


Config = ConfigParser.ConfigParser()
Config.read('./config.ini')

kafkaHost = Config.get('Kafka', 'host')
kafkaPort = Config.get('Kafka', 'port')
topic = Config.get('face-producer', 'topic')

recognizerFile= '/home/pi/facedetect/generated.rec'


cascade_path = '/home/pi/opencv-3.0.0/data/haarcascades/haarcascade_frontalface_default.xml'
eyes_path= '/home/pi/opencv-3.0.0/data/haarcascades/haarcascade_eye.xml'
noses_path= '/home/pi/opencv-3.0.0/data/haarcascades/Nariz.xml'

face_cascade = cv2.CascadeClassifier(cascade_path)
eye_cascade = cv2.CascadeClassifier(eyes_path)
nose_cascade = cv2.CascadeClassifier(noses_path)

# For face recognition we will the the LBPH Face Recognizer
recognizer = cv2.face.createLBPHFaceRecognizer()

show_windows=False


prediction_lower_limit = 80.
prediction_upper_limit = 100.

def really_a_face (inner_face):

    eyes = eye_cascade.detectMultiScale(inner_face, minSize=(10, 10))
    if len(eyes) >= 2 :

        if show_windows:

            for (ex,ey,ew,eh) in eyes[:2]:
                cv2.rectangle(inner_face,(ex,ey),(ex+ew,ey+eh),(255,0,0),2)

            cv2.imshow("Adding faces to traning set...", inner_face)
            cv2.waitKey(5)

        return True

    return False




def check_image(new_image):
    nbrs = []
    predict_image_pil = Image.open(new_image).convert('L')
    predict_image = np.array(predict_image_pil, 'uint8')
    faces = face_cascade.detectMultiScale(predict_image,
                                         scaleFactor=1.1,
                                         minNeighbors=5,
                                         minSize=(100, 100),
                                         flags = cv2.CASCADE_SCALE_IMAGE)
    for (x, y, w, h) in faces:
        inner_face= predict_image[y: y + h, x: x + w]

        if really_a_face(inner_face):
            resized= scipy.misc.imresize(inner_face, ( 100. / h ))
            nbr_predicted, conf = recognizer.predict(resized)
            print "nbr: {}, conf: {}".format(nbr_predicted, conf)

            if prediction_lower_limit <= conf <= prediction_upper_limit:
                nbrs.append(nbr_predicted)

    return nbrs






if __name__ == "__main__":

    if len(sys.argv) >= 2:
        show_windows=True

    if os.path.exists(recognizerFile):
        recognizer.load(recognizerFile)

        cam = picamera.PiCamera()
        producer = KafkaProducer(bootstrap_servers=kafkaHost+':'+kafkaPort)

        while True:
            image_file = '/tmp/face-detect.jpg'
            cam.capture(image_file)

            ids= check_image(image_file)

            if ids :
                print( strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ': found a face! {}'.format(ids))
                producer.send(topic, b'{"found" : true, "person": "any"}')

            os.remove(image_file)
            sleep(0.1)

        else:
            print "no recognizer found."

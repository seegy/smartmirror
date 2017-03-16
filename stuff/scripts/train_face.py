#!/usr/bin/python2.7

import sys
import time
import cv2, picamera, os, threading, logging, time, ConfigParser
from PIL import Image
import numpy as np
from io import BytesIO


cascade_path = '/home/pi/opencv-3.0.0/data/haarcascades/haarcascade_frontalface_default.xml'
eyes_path= '/home/pi/opencv-3.0.0/data/haarcascades/haarcascade_eye.xml'
noses_path= '/home/pi/opencv-3.0.0/data/haarcascades/Nariz.xml'

face_cascade = cv2.CascadeClassifier(cascade_path)
eye_cascade = cv2.CascadeClassifier(eyes_path)
nose_cascade = cv2.CascadeClassifier(noses_path)


def really_a_face (inner_face):

    eyes = eye_cascade.detectMultiScale(inner_face, minSize=(30, 30))
    if len(eyes) >= 2 :

        noses = nose_cascade.detectMultiScale(inner_face, minSize=(100, 30))

        if len(noses) >= 1 :

            return True
    return False


def find_a_face(image):

    image_pil= image.convert('L')
    # Convert the image format into numpy array
    image = np.array(image_pil, 'uint8')

    faces = face_cascade.detectMultiScale(
        image,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(200, 200),
        flags = cv2.CASCADE_SCALE_IMAGE
    )

    # iterate over all identified faces and try to find eyes
    for (x, y, w, h) in faces:

        inner_face= image[y:y+h, x:x+w]

        if really_a_face(inner_face):
            cv2.imshow("Recognizing Face", inner_face)
            cv2.waitKey(5)
            return inner_face





if __name__ == "__main__":


    if len(sys.argv) >= 2:
        id = sys.argv[1]

        path = os.path.join('/home/pi/train', id)

        if not os.path.exists(path):
            os.makedirs(path)

        cam = picamera.PiCamera()

        MAX_PICS = 100

        i=0
        while i < MAX_PICS:
            print "say Cheesee!"
            stream = BytesIO()
            cam.capture(stream, format='jpeg')
            stream.seek(0)
            image = Image.open(stream)

            face= find_a_face(image)

            if not face is None:
                ts = time.time()
                img = Image.fromarray(face)
                img.save(os.path.join(path, str(ts) + ".jpg"))
                i= i+1

           # sleep(0.01)
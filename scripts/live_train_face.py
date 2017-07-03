#!/usr/bin/env python

import sys
import cv2, picamera, os, threading, logging, time
from PIL import Image
import numpy as np
from io import BytesIO
from face_helper import Face_Helper

# In Python 3, ConfigParser has been renamed to configparser for PEP 8 compliance
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser


Config = ConfigParser.ConfigParser()
Config.read('./config.ini')
fh = Face_Helper()


def find_a_face(image):

    image_pil= image.convert('L')
    # Convert the image format into numpy array
    image = np.array(image_pil, 'uint8')

    faces = fh.detect_faces(image)

    # iterate over all identified faces and try to find eyes
    for (x, y, w, h) in faces:

        inner_face= image[y:y+h, x:x+w]
        if fh.really_a_face(inner_face):
            return inner_face


if __name__ == "__main__":


    if len(sys.argv) >= 2:
        id = sys.argv[1]

        path = os.path.join('/home/pi/train', id)

        if not os.path.exists(path):
            os.makedirs(path)

        cam = picamera.PiCamera()
        cam.rotation = Config.get('Camera', 'rotation')

        MAX_PICS = 100

        i=0
        print("say Cheesee!")
        while i < MAX_PICS:
            stream = BytesIO()
            cam.capture(stream, format='jpeg')
            stream.seek(0)
            image = Image.open(stream)

            face= find_a_face(image)

            if not face is None:
                ts = time.time()
                img = Image.fromarray(face)
                imgPath = os.path.join(path, str(ts) + ".jpg")
                img.save(imgPath)
                print('ok! ('+imgPath+')')
                fh.train_pictures([imgPath], int(id), True)
                print("say Cheesee!")
                i= i+1

           # sleep(0.01)
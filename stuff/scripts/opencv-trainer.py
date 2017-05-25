#!/usr/bin/python2.7

import sys
import cv2, os, threading, logging, time, ConfigParser
import numpy as np
from PIL import Image
import glob
import matplotlib.image as mpimg
import scipy.ndimage

recognizerDir= '/home/pi/facedetect/'
recognizerFile= recognizerDir + 'generated.rec'

cascade_path = '/home/pi/opencv-3.0.0/data/haarcascades/haarcascade_frontalface_default.xml'
eyes_path= '/home/pi/opencv-3.0.0/data/haarcascades/haarcascade_eye.xml'
noses_path= '/home/pi/opencv-3.0.0/data/haarcascades/Nariz.xml'

face_cascade = cv2.CascadeClassifier(cascade_path)
eye_cascade = cv2.CascadeClassifier(eyes_path)
nose_cascade = cv2.CascadeClassifier(noses_path)

# For face recognition we will the the LBPH Face Recognizer
recognizer = cv2.face.createLBPHFaceRecognizer()
update = False
basewidth = 300 #TODO ?

face_max_pixels= 80
detect_min_pixels= face_max_pixels

show_windows=True


def resize_image(inner_face):
    h= np.size(inner_face, 0)
    return scipy.misc.imresize(inner_face, ( (0. + face_max_pixels) / h ))


def really_a_face (inner_face):

    eyes = eye_cascade.detectMultiScale(inner_face, minSize=(10, 10))
    if len(eyes) >= 2 :

        noses = nose_cascade.detectMultiScale(inner_face, minSize=(10, 10))

        if (len(noses) >= 1):
            if show_windows:

                for (ex,ey,ew,eh) in eyes[:2]:
                    cv2.rectangle(inner_face,(ex,ey),(ex+ew,ey+eh),(255,0,0),2)

                cv2.imshow("Adding faces to traning set...", resize_image(inner_face))
                cv2.waitKey(5)

            return True

    return False


def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])

def train_pictures(image_paths, nbr, skipCheck):

    # images will contains face images
    images = []
    # labels will contains the label that is assigned to the image
    labels = []


    for image_path in image_paths:

        # Read the image and convert to grayscale
        image_pil = 0

        if image_path.upper().endswith('PNG') :
            #image_pil = misc.imread(image_path).face(gray=True)
            image_pil = rgb2gray(mpimg.imread(image_path))
        else :
            image_pil = Image.open(image_path).convert('L')
        # Convert the image format into numpy array
        image = np.array(image_pil, 'uint8')

        if skipCheck:
            images.append(image)
            labels.append(nbr)
            print "{}: Adding faces to traning set for {}...".format(image_path, nbr)

        else:
            # Detect the face in the image
            faces = face_cascade.detectMultiScale(image,
                                                  scaleFactor=1.1,
                                                  minNeighbors=5,
                                                  minSize=(detect_min_pixels, detect_min_pixels),
                                                  flags = cv2.CASCADE_SCALE_IMAGE)
            # If face is detected, append the face to images and the label to labels
            for (x, y, w, h) in faces:
                inner_face= image[y: y + h, x: x + w]

                if really_a_face(inner_face):
                    resized= resize_image(inner_face)
                    images.append(resized)
                    labels.append(nbr)
                    #print "{} {} {} {} {}: Adding faces to traning set for {}...".format(image_path, y, h, x, w, nbr)

    print "Add {} samples to id {}.".format(len(labels), nbr)
    # return the images list and labels list
    if update:
        recognizer.update(images, np.array(labels))
    else:
        recognizer.train(images, np.array(labels))

    return images, labels



if __name__ == "__main__":

    skipCheck=False

    if len(sys.argv) >= 3:
        nbr = sys.argv[1]
        image_path = sys.argv[2]


        if len(sys.argv) >= 4 and sys.argv[3] == '-skipCheck':
            skipCheck= True


        file_list = []

        if os.path.exists(recognizerFile):
            recognizer.load(recognizerFile)
            print "found existing model!"
            update= True

        if os.path.exists(image_path):

            if os.path.isfile(image_path):
                file_list.append(image_path)
                train_pictures(file_list, int(nbr), skipCheck)

            elif os.path.isdir(image_path):
                file_list= glob.glob(image_path +"/*")
                train_pictures(file_list, int(nbr), skipCheck)

            elif glob.glob(image_path).length:
                file_list= glob.glob(image_path)
                train_pictures(file_list, int(nbr), skipCheck)

            else:
                print "file not found"

        if not os.path.exists(recognizerDir):
            os.makedirs(recognizerDir)
        recognizer.save(recognizerFile)

    else:
        print "useage: <script> <nbr> <file/dir>"

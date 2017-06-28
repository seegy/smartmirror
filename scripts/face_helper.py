#!/usr/bin/python2.7

import cv2, os
import numpy as np
from PIL import Image
import scipy.ndimage
import matplotlib.image as mpimg
import ConfigParser

Config = ConfigParser.ConfigParser()
Config.read('./config.ini')

class Face_Helper:


    def __init__(self):

        self.recognizerDir= '/home/pi/facedetect/'
        self.recognizerFile= self.recognizerDir + 'generated.rec'

        cascade_path = Config.get('OpenCV', 'cascade_path')
        eyes_path= Config.get('OpenCV', 'eyes_path')
        noses_path= Config.get('OpenCV', 'noses_path')

        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.eye_cascade = cv2.CascadeClassifier(eyes_path)
        self.nose_cascade = cv2.CascadeClassifier(noses_path)

        # For face recognition we will the the LBPH Face Recognizer
        self.recognizer = cv2.face.createLBPHFaceRecognizer()

        if os.path.exists(self.recognizerDir):
            self.set_recognizer(self.recognizerFile)

        self.face_max_pixels= 80

        self.prediction_lower_limit = 80.
        self.prediction_upper_limit = 120.


    def really_a_face (self, inner_face, show_windows=False):
        eyes = self.eye_cascade.detectMultiScale(inner_face, minSize=(10, 10))
        if len(eyes) >= 2 :
            if show_windows:

                for (ex,ey,ew,eh) in eyes[:2]:
                    cv2.rectangle(inner_face,(ex,ey),(ex+ew,ey+eh),(255,0,0),2)

                cv2.imshow("Adding faces to traning set...", inner_face)
                cv2.waitKey(5)

            return True
        return False



    def rgb2gray(self, rgb):
        return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])



    def resize_image(self, inner_face):
        h= np.size(inner_face, 0)
        return scipy.misc.imresize(inner_face, ( (0. + self.face_max_pixels) / h ))

    def set_recognizer(self, recognizerFile):
        self.recognizer.load(recognizerFile)


    def detect_faces(self, predict_image):
        return self.face_cascade.detectMultiScale(predict_image,
                                                  scaleFactor=1.1,
                                                  minNeighbors=5,
                                                  minSize=(self.face_max_pixels, self.face_max_pixels),
                                                  flags = cv2.CASCADE_SCALE_IMAGE)

    def find_nbrs(self, new_image):
        nbrs = []
        faces = self.detect_faces(new_image)

        for (x, y, w, h) in faces:
            inner_face= new_image[y: y + h, x: x + w]

            if self.really_a_face(inner_face):
                resized= self.resize_image(inner_face)
                nbr_predicted, conf = self.recognizer.predict(resized)
                print "nbr: {}, conf: {}".format(nbr_predicted, conf)

                if self.prediction_lower_limit <= conf <= self.prediction_upper_limit:
                    nbrs.append(nbr_predicted)
        return nbrs




    def train_pictures(self, image_paths, nbr, skipCheck=False):
        # images will contains face images
        images = []
        # labels will contains the label that is assigned to the image
        labels = []

        for image_path in image_paths:
            # Read the image and convert to grayscale
            image_pil = 0

            if image_path.upper().endswith('PNG'):
                image_pil = self.rgb2gray(mpimg.imread(image_path))
            else:
                image_pil = Image.open(image_path).convert('L')

            # Convert the image format into numpy array
            image = np.array(image_pil, 'uint8')

            if skipCheck:
                images.append(image)
                labels.append(nbr)
                print "{}: Adding faces to traning set for {}...".format(image_path, nbr)

            else:
                # Detect the face in the image
                faces = self.detect_faces(image)

                # If face is detected, append the face to images and the label to labels
                for (x, y, w, h) in faces:
                    inner_face= image[y: y + h, x: x + w]

                    if self.really_a_face(inner_face):
                        resized= self.resize_image(inner_face)
                        images.append(resized)
                        labels.append(nbr)
                        #print "{} {} {} {} {}: Adding faces to traning set for {}...".format(image_path, y, h, x, w, nbr)

        print "Add {} samples to id {}.".format(len(labels), nbr)
        # return the images list and labels list
        if os.path.exists(self.recognizerFile):
            self.recognizer.update(images, np.array(labels))
        else:
            self.recognizer.train(images, np.array(labels))

        return images, labels

    def save(self):
        if not os.path.exists(self.recognizerDir):
            os.makedirs(self.recognizerDir)
        self.recognizer.save(self.recognizerFile)
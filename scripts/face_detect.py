#!/usr/bin/python2.7

import sys
from time import sleep, gmtime, strftime
import ConfigParser
import redis
from face_helper import Face_Helper
from io import BytesIO
from PIL import Image
import numpy as np
import argparse


from scipy.misc import imread
from scipy.linalg import norm
from scipy import sum, average


parser = argparse.ArgumentParser(description='face detection application. requires Redis!')

parser.add_argument('--show_delta', action="store_true", help='Shows the movement delta image')
parser.add_argument('--show_detection', action="store_true", help='Shows detected faces.')
parser.add_argument('--show_cam', action="store_true", help='Shows cam snapshot.')
parser.add_argument('--show_all', action="store_true", help='Shows all')


Config = ConfigParser.ConfigParser()
Config.read('./conf/config.ini')


config = {
    'host': Config.get('Redis', 'host'),
    'port': Config.get('Redis', 'port'),
    'db': Config.get('Redis', 'db'),
}

r = redis.StrictRedis(**config)
channel = Config.get('face-producer', 'channel')
fh = Face_Helper()

args = None

# TODO
#import picamera
#cam = picamera.PiCamera()


# how much must a pixel has to change the be marked as "changed"
threshold = 10000
# how many times takes the checker without any motion a face in front of the cam for possible
person_timeout_limit= 10
aperture_time = 0.15

import cv2


def get_image():

    cap = cv2.VideoCapture(0)
    result = None
    sleep(aperture_time)
    ret, frame = cap.read()
    cap.release()

    if ret:
        result = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #result = frame

    return result



def check_motion(old_image, new_image):

    frameDelta = cv2.absdiff(old_image, new_image)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
    #thresh = cv2.dilate(thresh, None, iterations=2)

    white_count = cv2.countNonZero(thresh)
    pixel_count = thresh.size

    percent_movement = (0.0 + white_count) / pixel_count

    if args.show_all or args.show_delta:
        cv2.imshow('Movement delta',thresh)
        cv2.waitKey(5)
        cv2.destroyAllWindows()

    return percent_movement >= 0.1



if __name__ == "__main__":

    args = parser.parse_args()


    last_image=get_image()
    last_time_face_seen= False
    last_ids=[]
    person_timeout_counter= 0
    first_interval = True

    while True:

        image = get_image()
        was_motion= check_motion(last_image, image)

        if was_motion or first_interval:
            print( 'motion detected!')
            ids= fh.find_nbrs(image, show_faces=(args.show_all or args.show_detection), show_cam=(args.show_all or args.show_cam))

            print "ids: {}".format(ids)

            if ids:
                person_timeout_counter = 0
                last_time_face_seen=True
                last_ids= ids
                print( strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ': found a face! {}'.format(ids))
                r.publish(channel, '{"found" : true, "person": ' + str(ids) + '}')

            else:
                last_time_face_seen=False

        else:
            print( 'no motion detected')

            if last_time_face_seen:
                person_timeout_counter +=1
                print( strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ': still face there {}'.format(ids))
                r.publish(channel, '{"found" : true, "person": ' + str(ids) + '}')

                if person_timeout_counter >= person_timeout_limit:
                    ids= fh.find_nbrs(image)

                    if ids:
                        print( strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ': still face there {} (refreshed)'.format(ids))
                        person_timeout_counter = 0
                        last_time_face_seen=True
                        last_ids= ids
                    else:
                        last_time_face_seen=False

            else:
                sleep(0.5)


        first_interval = False
        last_image = image
        sleep(0.5)

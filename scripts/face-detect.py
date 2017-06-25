#!/usr/bin/env python

import sys
from time import sleep, gmtime, strftime
import picamera
import redis
from face_helper import Face_Helper
from io import BytesIO
from PIL import Image
import numpy as np

# In Python 3, ConfigParser has been renamed to configparser for PEP 8 compliance
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser


Config = ConfigParser.ConfigParser()
Config.read('./config.ini')


config = {
    'host': Config.get('Redis', 'host'),
    'port': Config.get('Redis', 'port'),
    'db': Config.get('Redis', 'db'),
}

r = redis.StrictRedis(**config)
channel = Config.get('face-producer', 'channel')
fh = Face_Helper()
show_windows=False
cam = picamera.PiCamera()


# how many percent of pixel will be checked
check_percentage = 0.05
# how much must a pixel has to change the be marked as "changed"
threshold = 5
# how many percent of pixels in the image must marked as "changed" to declare a motion
sensitivity = 0.02
# how many times takes the checker without any motion a face in front of the cam for possible
person_timeout_limit= 10


def get_image():
    stream = BytesIO()
    cam.capture(stream, format='jpeg')
    stream.seek(0)
    return np.array(Image.open(stream).convert('L'), 'uint8')


def check_motion(old_image, new_image):

    changed=0
    size_x=len(old_image)
    size_y=len(old_image[0])
    sense_cap= size_x * size_y * sensitivity * check_percentage

    for x in xrange(0, size_x - 1, int(1/ check_percentage)):
        for y in xrange(0, size_y - 1, int(1 / check_percentage)):
            diff= abs(old_image[x,y] - new_image[x,y])
            if diff >= threshold:
                changed += 1

                if changed >= sense_cap:
                    return True
    return False



if __name__ == "__main__":

    if len(sys.argv) >= 2:
        show_windows=True


    last_image=get_image()
    last_time_face_seen= False
    last_ids=[]
    person_timeout_counter= 0

    while True:

        image = get_image()
        was_motion= check_motion(last_image, image)

        if was_motion:
            #print( 'motion detected!')
            ids= fh.find_nbrs(image)

            if ids:
                person_timeout_counter = 0
                last_time_face_seen=True
                last_ids= ids
                print( strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ': found a face! {}'.format(ids))
                r.publish(channel, '{"found" : true, "person": ' + str(ids) + '}')

            else:
                last_time_face_seen=False

        else:
            #print( 'no motion detected')

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



        last_image = image
        sleep(1)

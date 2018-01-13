#!/usr/bin/python2.7

import ConfigParser
import redis
import sys
import argparse
import pickle
import cv2
from time import sleep
import uuid
import scipy.misc



parser = argparse.ArgumentParser(description='saves unknown faces to related profiles by user io')


Config = ConfigParser.ConfigParser()
Config.read('./conf/config.ini')

config = {
    'host': Config.get('Redis', 'host'),
    'port': Config.get('Redis', 'port'),
    'db': Config.get('Redis', 'db'),
}

r = redis.StrictRedis(**config)

ufl = Config.get('Redis', 'unknown_face_list')

profile_list = Config.get('Redis', 'profile_list')
profile_prefix = Config.get('Redis', 'profile_prefix')
profile_id_attr = Config.get('Redis', 'profile_id_attr')
profile_path_attr = Config.get('Redis', 'profile_path_attr')
profile_name_attr = Config.get('Redis', 'profile_name_attr')


profile_legend = {}


def get_image_from_redis():
    raw_image = r.lpop(ufl)

    if raw_image is not None:
        image = pickle.loads(raw_image)
        return image

    return None



def init_profile_legend():

    profileset = r.smembers(profile_list)

    ks = [profile_path_attr, profile_name_attr]

    for pid in profileset :
        name = profile_prefix + ":" + pid

        profile = r.hmget(name, ks)

        profile_legend[pid] = {
            profile_path_attr : profile[0],
            profile_name_attr : profile[1]
        }


def show_profile_legend() :

    print "Following profiles exists (id -> name):"

    for pid, profile in profile_legend.items():
        print "{} -> {}".format(pid, profile[profile_name_attr])


def promt_loop():

    image = get_image_from_redis()

    while image is not None:

        cv2.destroyAllWindows()
        cv2.imshow('Who is this?', image)
        cv2.waitKey(5)

        input_string = raw_input("What to do with this image?\n(number -> put to profile, r -> remove, l -> show profile legend, q -> put image back and quit script): ")

        if input_string is "q" :
            r.lpush(ufl, pickle.dumps(image))
            break

        elif input_string is "l":
            show_profile_legend()
            continue

        elif input_string is "r":
            image = get_image_from_redis()
            continue

        elif input_string.isdigit():
            num = int(input_string)

            if profile_legend[input_string] is not None:
                print "adding to {}.".format(profile_legend[input_string][profile_name_attr])
                uid = str(uuid.uuid4())
                scipy.misc.imsave(profile_legend[input_string][profile_path_attr] + "/" + uid + ".jpg", image)

                image = get_image_from_redis()
            else:
                print "Unknown ID."
                continue
        else:
            print "Unknown command."
            continue

        print "All done!"



if __name__ == "__main__":

    args = parser.parse_args()


    llen = r.llen(ufl)

    print "There are {} unknown faces at the moment.".format(llen)

    if llen > 0 :
        print "things to do"
        init_profile_legend()
        show_profile_legend()

        promt_loop()

    else:
        print "Nothing to do."

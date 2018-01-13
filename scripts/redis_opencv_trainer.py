#!/usr/bin/python2.7

import sys
import cv2, os, threading, logging, time, ConfigParser, shutil
import glob
from face_helper import Face_Helper
import argparse
import redis

parser = argparse.ArgumentParser(description='Creates a trained model for face recognation')

parser.add_argument('--rm_existing', action="store_true", help='remove exiting model before train a new one.')
parser.add_argument('--skip_check', action="store_true", help='skip the face detection before every picture when training')
parser.add_argument('--show_faces', action="store_true", help='show trained faces, if check will not be skipped.')
parser.add_argument('--wait_for_nl', action="store_true", help='waits after every image (when shown) for new line')


Config = ConfigParser.ConfigParser()
Config.read('./conf/config.ini')


config = {
    'host': Config.get('Redis', 'host'),
    'port': Config.get('Redis', 'port'),
    'db': Config.get('Redis', 'db'),
}

profile_list = Config.get('Redis', 'profile_list')
profile_prefix = Config.get('Redis', 'profile_prefix')

profile_id_attr = Config.get('Redis', 'profile_id_attr')
profile_path_attr = Config.get('Redis', 'profile_path_attr')

redis_conn = redis.StrictRedis(**config)


fh = Face_Helper()

if __name__ == "__main__":

    args = parser.parse_args()

    if args.rm_existing and os.path.exists(fh.recognizerFile):
        print 'Removing existing.'
        shutil.rmtree(fh.recognizerDir)

    profileset = redis_conn.smembers(profile_list)

    ks = [profile_id_attr, profile_path_attr]
    list_to_train = []

    for pid in profileset :
        name = profile_prefix + ':' + pid

        list_to_train.append(redis_conn.hmget(name, ks))

    print list_to_train

    for face_id, dir_path in list_to_train:

        if os.path.isdir(dir_path):
            file_list= glob.glob(dir_path +"/*")
            fh.train_pictures(file_list, int(face_id), skipCheck=args.skip_check, show_windows=args.show_faces, wait_for_nl=args.wait_for_nl)
            fh.save()

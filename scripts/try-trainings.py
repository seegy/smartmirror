#!/usr/bin/python2.7

import sys
import os, ConfigParser
import glob
from face_helper import Face_Helper
import redis
from PIL import Image
import matplotlib.image as mpimg
import numpy as np
import itertools
import argparse

parser = argparse.ArgumentParser(description='Try different configurations of the face recognizer to get the best score.')

parser.add_argument('-dir', action='store', dest='anti_test_dir',
                    help='Path to directory of negative prediction images.')


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

percent_training_data = 0.20

def get_people_data():
    profileset = redis_conn.smembers(profile_list)

    ks = [profile_id_attr, profile_path_attr]
    list_to_train = []

    for pid in profileset :
        name = profile_prefix + ':' + pid

        list_to_train.append(redis_conn.hmget(name, ks))

    print list_to_train

    people = {}

    for face_id, dir_path in list_to_train:

        if os.path.isdir(dir_path):
            file_list= glob.glob(dir_path +"/*")

            abs_training_size = int(percent_training_data * len(file_list))

            people[int(face_id)] = {
                'train': file_list[:-abs_training_size],
                'test': file_list[-abs_training_size:]
            }

    return people

def get_anti_test_paths(path_to_dir):
    file_list= glob.glob(path_to_dir +"/*")
    return file_list


def train(fh, people):

    for nbr, data in people.iteritems():
        fh.train_pictures(data['train'], nbr)


def predict(fh, people):
    results = []

    for nbr, data in people.iteritems():
        for image_path in data['test']:
            image_pil = 0

            if image_path.upper().endswith('PNG'):
                image_pil = self.rgb2gray(mpimg.imread(image_path))
            else:
                image_pil = Image.open(image_path).convert('L')

            # Convert the image format into numpy array
            image = np.array(image_pil, 'uint8')

            result_nbrs = fh.find_nbrs(image, send_to_redis=False,silent=True)

            results.append({
                'nbr' : nbr,
                'image' : image_path,
                'predicted?' : nbr in result_nbrs,
                'prediction' : result_nbrs
            })

    return results

def anti_predict(fh, file_list):

    results = []

    for image_path in file_list:

        image_pil = 0

        if image_path.upper().endswith('PNG'):
            image_pil = self.rgb2gray(mpimg.imread(image_path))
        else:
            image_pil = Image.open(image_path).convert('L')

        # Convert the image format into numpy array
        image = np.array(image_pil, 'uint8')

        result_nbrs = fh.find_nbrs(image, send_to_redis=False,silent=True)

        results.append({
            'nbr' : 0,
            'image' : image_path,
            'predicted?' : len(result_nbrs) == 0,
            'prediction' : result_nbrs
        })

    return results


if __name__ == "__main__":

    args = parser.parse_args()

    if args.anti_test_dir is None:
        parser.print_help()
        exit()

    people = get_people_data()
    # print people
    anti_images = get_anti_test_paths(args.anti_test_dir)
    # print anti_images

    num_tests= reduce(lambda y,z: y+z, map(lambda x: len(people[x]['test']), people))
    num_anti_tests= len(anti_images)


    face_max_pixels_range = range(25, 250, 25)
    prediction_lower_limit_range = range (30, 90, 5)
    prediction_upper_limit_range = range(35, 120, 5)

    end_results = []

    for face_max_pixels in face_max_pixels_range:

        fh = Face_Helper()
        fh.face_max_pixels = face_max_pixels
        train(fh, people)

        for i in itertools.product(prediction_lower_limit_range,
         prediction_upper_limit_range):

            prediction_lower_limit= i[0]
            prediction_upper_limit= i[1]

            if prediction_lower_limit >= prediction_upper_limit:
                continue

            fh.prediction_lower_limit = prediction_lower_limit
            fh.prediction_upper_limit = prediction_upper_limit

            predictions = predict(fh, people)
            positive_count = len(filter(lambda a: a['predicted?'], predictions))

            anti_predictions = anti_predict(fh, anti_images)
            anti_positive_count = len(filter(lambda a: a['predicted?'], anti_predictions))

            end_results.append({
                'score': positive_count + anti_positive_count,
                'positive_score' : positive_count,
                'anti_positive_score' : anti_positive_count,
                'prediction_lower_limit' : prediction_lower_limit,
                'prediction_upper_limit': prediction_upper_limit,
                'face_max_pixels' : face_max_pixels
            })



            sys.stdout.write('{}-'.format(positive_count + anti_positive_count))
            sys.stdout.flush()

    end_results = sorted(end_results, key=lambda x: x['score'], reverse=True)

    print ' '
    print "Number of positive tests: {}, number of negative tests: {}, total possible score: {}".format(num_tests, num_anti_tests, (num_tests + num_anti_tests))

    for r in end_results[:10]:
        print r

#!/usr/bin/python2.7

import ConfigParser
import redis
import yaml
import sys

def progress_dot():
    sys.stdout.write('.')
    sys.stdout.flush()

Config = ConfigParser.ConfigParser()
Config.read('./conf/config.ini')

config = {
    'host': Config.get('Redis', 'host'),
    'port': Config.get('Redis', 'port'),
    'db': Config.get('Redis', 'db'),
}

r = redis.StrictRedis(**config)

profile_yaml = open('./conf/profiles.yml')
profiles = yaml.load(profile_yaml)

for p in profiles:

    if r.hmset("profile:" + str(p['faceId']), p):
        progress_dot()


if r.sadd('profiles', *set( map( lambda p : p['faceId'], profiles))):
    progress_dot()


if r.bgsave():
    print "\nPushed and saved."

profileset = r.smembers('profiles')

ks = None

for pid in profileset :
    name = 'profile:' + pid

    if not ks:
        ks = r.hkeys(name)
        print ks

    print r.hmget(name, ks)

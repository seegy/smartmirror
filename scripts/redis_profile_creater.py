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

profile_list = Config.get('Redis', 'profile_list')
profile_prefix = Config.get('Redis', 'profile_prefix')
profile_id_attr = Config.get('Redis', 'profile_id_attr')


r = redis.StrictRedis(**config)

profile_yaml = open('./conf/profiles.yml')
profiles = yaml.load(profile_yaml)

for p in profiles:

    if r.hmset(profile_prefix + ":" + str(p[profile_id_attr]), p):
        progress_dot()


if r.sadd(profile_list, *set( map( lambda p : p[profile_id_attr], profiles))):
    progress_dot()


if r.bgsave():
    print "\nPushed and saved."

profileset = r.smembers(profile_list)

ks = None

for pid in profileset :
    name = profile_prefix + ":" + pid

    if not ks:
        ks = r.hkeys(name)
        print ks

    print r.hmget(name, ks)

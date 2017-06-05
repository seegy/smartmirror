# Raspberry Smartmirror

This repository works as gathering for a smart/magic mirror applications based on the [RaspberryPi Model 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/). Every single IOP application, mostly Python scripts, are working as an autonomous cell and delivers its informations to one local Redis. Subsricers, such as monitors or output applications, get their data basically from Redis and process them by their own.


## Architecture

Currently, there are three types of components: data deliverer, processer and consumer. Deliverer are tools that grab data from the internet or via GPIO (Data-Crawler ```data-crawler```, Raspberry Cam Script ```scripts/face-detect.py```). 

As processer is Redis in use. The pubsub system is in use for the deliverer to send their data typeless to the consumers.

There is currently one consumer in the architecture. The GUI-Server takes messages from Redis PubSub and pushes them onto the GUI.

### Components

+ ```data-crawler``` clojure application to gather data (weather, train, ...) and push it into redis pubsub
+ ```face-detect``` a python script that uses the RaspberryPi camera and tries to recognize kown face. In case of found, it pushes a massage into Redis.
+ ```redis``` no custom system. Just a plain redis.
+ ```GUI-Server``` a NodeJS application with [electron](https://electron.atom.io/) GUI.

### Also in this repository
OpenCV is in use for face detection and recognation. So there are two scripts to train a recognation model:

+ ```scripts/opencv-trainer.py``` a script that takes a picture or a folder of pictures and an ID of a person to train (and create if nessessary) the recognation model.
+ ```scripts/live_train_face.py``` as script that use the RaspberryPi camera to take live pictures to train the recognation model for a person.


## Install introductions

For the installation, you need just one (better two) RaspberryPi with internet connection. Following components should be installed:

+ [Redis](http://mjavery.blogspot.de/2016/05/setting-up-redis-on-raspberry-pi.html)
+ [OpenCV](http://www.pyimagesearch.com/2016/04/18/install-guide-raspberry-pi-3-raspbian-jessie-opencv-3/)
+ [Leiningen](https://leiningen.org/)
+ [NodeJS](https://nodejs.org/en/)



```shell
# create config file
cp data-crawler/config.clj.sample data-crawler/config.clj
# customize configs
vi data-crawler/config.clj 

# start environment
sh startup.sh
```

### Optional


#### No screen blanking on GUI server

Change two lines in ```/etc/kbd/config```:

+ ```BLANK_TIME=0``` (was 30)
+ ```POWERDOWN_TIME=0``` (was 15)

Insert one line in ```/etc/lightdm/lightdm.conf``` under ```[SeatDefault]```:

+ ```xserver-command=X -s 0 dpms```


#### Hide mouse curser on GUI server

```shell
sudo apt-get install unclutter
# add 'unclutter -display :0 -noevents -grab &' into /etc/rc.local 
```

## TODOs
+ Use Redis data store to gather user profiles for interests. So the mirror should match a face to a profile and decides, which train connections or weather reports will be shown.
+ Interface for 'mirror admins' to create easily new profiles (via APP or Webservice).
+ GUI Module and data deliverer for Google Calendar
+ ansible script for role-based installation

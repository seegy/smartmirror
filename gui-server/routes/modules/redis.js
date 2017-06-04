const redis = require("redis");
const hash = require('object-hash');
const globalConfig = require('../../config/globalconf.json');
const redisConfig = globalConfig.redis;


function addChannelListender(chan, callback){

  let sub = redis.createClient(redisConfig.port, redisConfig.host);

  sub.on('message',  (channel, message) =>  {
    let parsed = JSON.parse(message);
    parsed.hash = hash(parsed);
    callback(channel, parsed);
  });

  sub.on('error', (err) => {
    console.log('redis client makes problems:' + err);
    setTimeout(addTopicListender(chan, callback), 1000);
  });

  sub.subscribe(chan);
}

exports.addChannelListender = addChannelListender

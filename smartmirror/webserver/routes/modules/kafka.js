let kafka = require('kafka-node');
let globalConfig = require('../../config/globalconf.json');

let zookeeperUrl = globalConfig.kafka.zookeeper.url;
let clientId = globalConfig.kafka.clientId;


function addTopicListender (topic, callback, fromOffset=true) {
  let Consumer = kafka.Consumer;
  let client = new kafka.Client(zookeeperUrl, clientId);
  new Consumer(
      client,
      [
          { topic: topic}
      ],
      {
          autoCommit: false,
          fromOffset: fromOffset
      }
  ).on('message', function (message) {
      //console.log(message);
      let parsed = JSON.parse(message.value);
      callback(parsed);
  }).on('error', function (err) {
      console.log(err);

      // when consumer crushs, wait a second and start new consumer.
      setTimeout(addTopicListender(topic, callback, fromOffset), 1000);
  });
};



exports.addTopicListender = addTopicListender;

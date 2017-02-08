let kafka = require('kafka-node');
let globalConfig = require('../../config/globalconf.json');

let zookeeperUrl = globalConfig.kafka.zookeeper.url;
let clientId = globalConfig.kafka.clientId;

exports.addTopicListender = function (topic, callback, fromOffset=true) {
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
      console.log(message);
      let parsed = JSON.parse(message.value);
      callback(parsed);
  });
};

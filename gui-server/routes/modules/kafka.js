let kafka = require('kafka-node');
var hash = require('object-hash');
let globalConfig = require('../../config/globalconf.json');

let zookeeperUrl = globalConfig.kafka.zookeeper.url;
let clientId = globalConfig.kafka.clientId;


function addTopicListender(topic, callback, fromOffset = true) {
    let Consumer = kafka.Consumer;
    let client = new kafka.Client(zookeeperUrl, clientId);

    var offset = new kafka.Offset(client);

    offset.fetch([{
        topic: topic,
        partition: 0,
        time: -1,
        maxNum: 1
    }], function(err, data) {

        if (data) {
            new Consumer(
                client, [{
                    topic: topic,
                    offset: data[topic][0][0]
                }], {
                    autoCommit: false,
                    fromOffset: fromOffset
                }
            ).on('message', function(message) {
                //console.log(message);
                try {
                    let parsed = JSON.parse(message.value);
                    parsed.hash = hash(parsed);
                    callback(parsed);
                } catch (e) {
                    console.log('unparseable kafka msg: ' + e);
                }

            }).on('error', function(err) {
                console.log("error while using consumer: " + err);

                // when consumer crushs, wait a second and start new consumer.
                setTimeout(addTopicListender(topic, callback, fromOffset), 1000);
            });

        } else {
            console.log("Error while fetching offset: " + err);
        }

    });
};



exports.addTopicListender = addTopicListender;

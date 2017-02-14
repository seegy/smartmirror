let kafka = require('./kafka');
let globalConfig = require('../../config/globalconf.json');

let topics = globalConfig.kafka.topics;

exports.create = function(server) {
    let io = require('socket.io')(server);

    topics.forEach((t, i) => {
        kafka.addTopicListender(t, (msg) => {
            io.emit(t, msg);
        }, true);
    })
}

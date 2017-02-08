var io = require('socket.io')(3001);
var kafka = require('./kafka');
let globalConfig = require('../../config/globalconf.json');

let topics = globalConfig.kafka.topics;

topics.forEach((t, i) => {
  kafka.addTopicListender(t, (msg) => {
      io.emit(t, msg);
    }, false);
})

var http = require('http').Server(app);
var io = require('socket.io')(http);
var kafka = require('./kafka');


exports.startTrain = () => {
  kafka.addTopicListender("train-news", (msg) => {
    io.emit('train-news', msg);
  }, false);
}

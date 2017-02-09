

function startTime() {
    var today = new Date();
    var h = today.getHours();
    var m = today.getMinutes();
    var d = today.getDate();
    var mo = today.getMonth() + 1;
    var y = today.getFullYear();
    var wd = today.getDay();

    m = checkTime(m);
    d = checkTime(d);
    mo = checkTime(mo);

    var days = ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"];
    wd = days[wd]

      $('#clock').html( h + ":" + m);
      $('#date').html( wd +" " + d + "." + mo + "." + y);
    var t = setTimeout(startTime, 1000);
}
function checkTime(i) {
    if (i < 10) {i = "0" + i};  // add zero in front of numbers < 10
    return i;
}



var socket = io('http://localhost:3001');

socket.on('train-news', function(msg){
   console.log(msg);
  // console.log(msg[0]);

  if(msg !== null && typeof msg !== 'object'){
    msg = JSON.parse(msg);
  }


  //  complete message?
  if( msg.to == "Frankfurt(Main)West" && msg.from == "Gießen Licher Str") {
// TODO ask for a real change!
    var newContent = new Array();

    msg.data.forEach(function(e,i,a){
      newContent[i] = '<table><tbody>';

      e.forEach(function(e1, i1, a1) {

        if(e.length >= 4 && i1 > 0 && i1 < e.length - 1){

          newContent[i] += '<tr>';
          newContent[i] += '<td class="train-times"></td>';
          newContent[i] += '<td class="train-delay"> ... </td>';
          newContent[i] += '<td class="train-station"></td>';
          newContent[i] += '<tr>';

        } else e1.forEach(function(e2, i2, a2){

          newContent[i] += '<tr>';
          newContent[i] += '<td class="train-times">' + e2['time'] + '</td>';
          newContent[i] += '<td class="train-delay">' + e2['delay'] + '</td>';
          newContent[i] += '<td class="train-station">' + e2['station'] + '</td>';
          newContent[i] += '<tr>';
        });

        newContent[i] += '<tr>';
        newContent[i] += '<td class="train-times"><div class="seperator line" ></div> </td>';
        newContent[i] += '<tr>';
      });

      newContent[i] += '</tbody></table>';
    });

    var trainEles = ['.firstTrain', '.secondTrain']

    trainEles.forEach(function(e,i,a){
      $(e).empty();
      $(e).append(newContent[i]);
    });

  }
});


var iconMatch = {
  "01d" : "B",
  "02d" : "H",
  "03d" : "N",
  "04d" : "Y",
  "09d" : "Q",
  "10d" : "R",
  "11d" : "P",
  "13d" : "W",
  "50d" : "M",
  "01n" : "C",
  "02n" : "I",
  "03n" : "N",
  "04n" : "Y",
  "09n" : "Q",
  "10n" : "R",
  "11n" : "P",
  "13n" : "W",
  "50n" : "M"
};

socket.on('weather-news', function(msg){

  if(msg !== null && typeof msg !== 'object'){
    msg = JSON.parse(msg);
  }

  console.log(msg);

  if(msg.location == "giessen"){
    var owmIcon = msg.data.weather[0].icon;
    var temp = msg.data.main.temp;
    $('#headWeatherIcon').attr("data-icon", iconMatch[owmIcon]);
    $('#headTemp').html(temp.toFixed(1));
  }
});

socket.on('weather-forecast', function(msg){
  if(msg !== null && typeof msg !== 'object'){
    msg = JSON.parse(msg);
  }

  console.log(msg);

});



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

    document.getElementById('clock').innerHTML
      = h + ":" + m + "<br>"+ wd +" " + d + "." + mo + "." + y;
    var t = setTimeout(startTime, 1000);
}
function checkTime(i) {
    if (i < 10) {i = "0" + i};  // add zero in front of numbers < 10
    return i;
}



var socket = io('http://localhost:3001');

socket.on('train-news', function(msg){
  // console.log(msg);
  // console.log(msg[0]);

  //  complete message?
  if( msg.length == 3) {
// TODO ask for a real change!
    var newContent = new Array();

    msg.forEach(function(e,i,a){
      newContent[i] = '<table><tbody>';

      e.forEach(function(e1, i1, a1) {

        if(e.length >= 4 && i1 > 0 && i1 < e.length - 1){

          newContent[i] += '<tr>';
          newContent[i] += '<td class="train-times"></td>';
          newContent[i] += '<td> ... </td>';
          newContent[i] += '<td class="station"></td>';
          newContent[i] += '<tr>';

        } else e1.forEach(function(e2, i2, a2){

          newContent[i] += '<tr>';
          newContent[i] += '<td class="train-times">' + e2['time'] + '</td>';
          newContent[i] += '<td>' + e2['delay'] + '</td>';
          newContent[i] += '<td class="station">' + e2['station'] + '</td>';
          newContent[i] += '<tr>';
        });

        newContent[i] += '<tr>';
        newContent[i] += '<td class="train-times"><div class="seperator" ></div> </td>';
        newContent[i] += '<tr>';
      });

      newContent[i] += '</tbody></table>';
    });

    var trainEles = ['.firstTrain', '.secondTrain', '.thirdTrain']

    trainEles.forEach(function(e,i,a){
      $(e).empty();
      $(e).append(newContent[i]);
    });

  }
});

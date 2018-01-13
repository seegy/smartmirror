var DEBUG = false;
var scrollInterval = 5000; // ms
var hideInterval = 6000;


var people = {
  1: "S&ouml;ren",
  2: "Silvia"
}


var days = ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"];

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


  wd = days[wd]

  $('#clock').html(h + ":" + m);
  $('#date').html(wd + " " + d + "." + mo + "." + y);
  var t = setTimeout(startTime, 1000);
}

function checkTime(i) {
  if (i < 10) {
    i = "0" + i
  }; // add zero in front of numbers < 10
  return i;
}

function replaceAll(str, find, replace) {
  return str.replace(new RegExp(find, 'g'), replace);
}

function getAppendParent() {
  return $('.module-hook');
}

var moduleCount = 0;

function appendModule(html) {

  console.log("add module");
  var hook = getAppendParent();

  html = "<li>" + html + "</li>";

  if (moduleCount++ == 0) {
    // make first one active
    //html = $.parseHTML(html);
    //html.addClass('active');
    //html[0].className += ' active';
    //console.log(html);
  }

  hook.append(html);
  resetCarousel();
}


var iconMatch = {
  "01d": "B",
  "02d": "H",
  "03d": "N",
  "04d": "Y",
  "09d": "Q",
  "10d": "R",
  "11d": "P",
  "13d": "W",
  "50d": "M",
  "01n": "C",
  "02n": "I",
  "03n": "N",
  "04n": "Y",
  "09n": "Q",
  "10n": "R",
  "11n": "P",
  "13n": "W",
  "50n": "M"
};

function degToCompass(num) {
  var val = Math.floor((num / 22.5) + 0.5);
  var arr = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"];
  return arr[(val % 16)];
}


var hideTime = new Date();

function hideEverything() {

  if (DEBUG) {
    return;
  }

  var main = $('div.main');
  var now = new Date();

  if (hideTime < now) {
    stopCarousel()
    $('div.main').hide(500);
    //$('div.main').attr('display', 'none !important');
  } else {
    var diff = hideTime - now;
    setTimeout(hideEverything, diff);
  }
}

function putName(msgPeople) {
  if (msgPeople == "any") { // unknown person
    $('#hello').html('Hallo, Fremder.')
  } else { // known person

    // matching the personid to a person
    if (msgPeople !== null && msgPeople instanceof Array) {
      msgPeople = [msgPeople];
    }

    var names = msgPeople.map(function(x) {
      return people[x];
    })
    names = names.join(' und ');

    $('#hello').html('Hallo, ' + names + '.')
  }

}


function setWidth(){
  //dynamic css
  let calculatedWidth = $('.main').height() / 16 * 9;

  $('.main').css({
    'width': calculatedWidth + 'px'
  });
  $('.main').css({
    'max-width': calculatedWidth + 'px'
  });
}




//########## init stuff #############

function init() {

  setWidth();
  setTimeout(hideEverything, 1000);

  startTime();

  var socket = io('http://localhost:3000');

  var PATH_TO_MODULE_LIST = "./modules/modules.json";

  $.ajax({
    url: PATH_TO_MODULE_LIST,
    success: function(data) {
      //console.log(data); // Data returned

      eval(data).forEach((m, i) => {
        //console.log(m);

        $.ajax({
          url: "./modules/" + m + "/main.js",
          dataType: "text",
          success: function(result) {

            // source: http://jsfiddle.net/rahilwazir/gfbAg/110/
            var data = new Object();
            data.func = result;
            var jsonVal = JSON.stringify(data);
            var newObj = $.parseJSON(jsonVal);
            eval(newObj.func);
            main(socket);
          }
        });
      });
    }
  });

  socket.on('weather-news', function(msg) {

    if (msg !== null && typeof msg !== 'object') {
      msg = JSON.parse(msg);
    }

    var wIcon = $('#headWeatherIcon');

    if (wIcon.attr('latest') != msg.hash) {
      var owmIcon = msg.data.weather[0].icon;
      var temp = msg.data.main.temp;
      wIcon.attr("data-icon", iconMatch[owmIcon]);
      wIcon.attr('latest', msg.hash);
      $('#headTemp').html(temp.toFixed(1));
    }
  });


  socket.on('faces', function(msg) {
    if (msg !== null && typeof msg !== 'object') {
      msg = JSON.parse(msg);
    }

    //{"found" : true, "person": "any"}

    if (msg.found) {

      putName(msg.person);

      // show the ui
      setWidth();
      $('div.main').show(500);
      resetCarousel();

      var newDateObj = new Date(new Date().getTime() + hideInterval);
      hideTime = newDateObj;

      setTimeout(hideEverything, hideInterval);
    }
  });
}


// ############ Carousel #############

let carouselEnabled = false;

function scroll() {
  //TODO skip more, if invisible objects are ahead
  if (carouselEnabled) {
    $('.jcarousel').jcarousel('scroll', '+=1');
    setTimeout(scroll, scrollInterval);
  }
}

function initCarousel() {
  var jcarousel = $('.jcarousel');
  jcarousel.jcarousel({
    wrap: 'circular',
    vertical: true
  })
  carouselEnabled = true;
  scroll();
}

function resetCarousel() {
  stopCarousel()
  $('.jcarousel').jcarousel('reload');
  carouselEnabled = true;
  scroll();
}

function stopCarousel(){
  carouselEnabled = false;
}


(function($) {
  $(function() {
    initCarousel()
  });
})(jQuery);

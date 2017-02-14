var DEBUG = false;
var scrollInterval = 5000; // ms
var hideInterval = 3000;


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
        console.log("hide!");
        $('div.main').hide(1000);
        //$('div.main').attr('display', 'none !important');
    } else {
        var diff = hideTime - now;
        setTimeout(hideEverything, diff);
    }
}




 //########## init stuff #############

function init() {

    setTimeout(hideEverything, 1000);

    startTime();

    var socket = io();

    socket.on('train-news', function(msg) {
        if (msg !== null && typeof msg !== 'object') {
            msg = JSON.parse(msg);
        }

        var mod = $("div[type='trains'][from='" + msg.from + "'][to='" + msg.to + "']");

        //  complete message?
        //if( msg.to == "Frankfurt(Main)West" && msg.from == "Gießen Licher Str") {
        // TODO ask for a real change!

        var fillData = function() {
            var newContent = new Array();

            msg.data.forEach(function(e, i, a) {
                newContent[i] = '<table><tbody>';

                e.forEach(function(e1, i1, a1) {

                    if (e.length >= 4 && i1 > 0 && i1 < e.length - 1) {

                        newContent[i] += '<tr>';
                        newContent[i] += '<td class="train-times"></td>';
                        newContent[i] += '<td class="train-delay"> ... </td>';
                        newContent[i] += '<td class="train-station"></td>';
                        newContent[i] += '<tr>';

                    } else e1.forEach(function(e2, i2, a2) {

                        newContent[i] += '<tr>';
                        newContent[i] += '<td class="train-times">' + e2['time'] + '</td>';
                        newContent[i] += '<td class="train-delay">' + e2['delay'] + '</td>';
                        newContent[i] += '<td class="train-station">' + e2['station'] + '</td>';
                        newContent[i] += '<tr>';
                    });

                    newContent[i] += '<tr>';
                    newContent[i] += '<td class="train-times"><div class="seperator line" ></div></td>';
                    newContent[i] += '<tr>';
                });

                newContent[i] += '</tbody></table>';
            });

            var trainEles = ['.firstTrain', '.secondTrain']

            trainEles.forEach(function(e, i, a) {
                $(e).empty();
                $(e).append(newContent[i]);
            });

            resetCarousel();
        }


        if (mod[0] === undefined) {
            console.log('module unknown for trains: ' + msg.from + ',' + msg.to);

            $.ajax({
                url: "/html/trains-modul.html",
                success: function(result) {

                    result = replaceAll(result, "###1###", msg.from)
                    result = replaceAll(result, "###2###", msg.to);


                    appendModule(result);
                    //getAppendParent().append(result)

                    mod = $("div[type='trains'][from='" + msg.from + "'][to='" + msg.to + "']");
                    mod.attr('latest', mod.hash);
                    fillData();
                }
            });

        } else if (mod.attr('latest') != mod.hash) {
            console.log("new data, changing view");
            mod.attr('latest', mod.hash);
            fillData();
        } else {
          //nothing to change...
        }
    });

    socket.on('weather-news', function(msg) {

        if (msg !== null && typeof msg !== 'object') {
            msg = JSON.parse(msg);
        }

        var wIcon = $('#headWeatherIcon');

        if (msg.location == "giessen" && wIcon.attr('latest') != msg.hash) {
            var owmIcon = msg.data.weather[0].icon;
            var temp = msg.data.main.temp;
            wIcon.attr("data-icon", iconMatch[owmIcon]);
            wIcon.attr('latest', msg.hash);
            $('#headTemp').html(temp.toFixed(1));
        }
    });

    socket.on('weather-forecast', function(msg) {
        if (msg !== null && typeof msg !== 'object') {
            msg = JSON.parse(msg);
        }

        var loc = msg.location.toUpperCase();
        var dat = msg.data;

        var mod = $("div[type='weather-forecast'][location='" + loc + "']");

        var fillData = function() {
            for (i = 0; i < 3; i++) {
                var submod = mod.find("div[order='" + i + "']")
                var data = dat[i]

                submod.find("a.icon.forecast").attr("data-icon", iconMatch[data.weather[0].icon])
                submod.find(".temp").html(data.main.temp.toFixed(1));
                submod.find(".humi").html(data.main.humidity.toFixed(1) + "%");
                submod.find(".wind").html(degToCompass(data.wind.deg));

                var today = new Date(data.dt * 1000);
                var wd = today.getDay();

                submod.find(".wd").html(days[wd]);
                resetCarousel();
            }
        }

        if (mod[0] === undefined) {
            console.log('module unknown for weather-forecast: ' + loc);

            $.ajax({
                url: "/html/weather-forecast-modul.html",
                success: function(result) {

                    result = result.replace("###1###", loc).replace("###2###", loc);

                    //getAppendParent().append(result)
                    appendModule(result);

                    mod = $("div[type='weather-forecast'][location='" + loc + "']");
                    mod.attr('latest', mod.hash);
                    fillData();
                }
            });

        } else if (mod.attr('latest') != mod.hash) {
            console.log("new data, changing view");
            mod.attr('latest', mod.hash);
            fillData();
        } else {
            // nothing to change...
        }
    });

    socket.on('faces', function(msg) {
        if (msg !== null && typeof msg !== 'object') {
            msg = JSON.parse(msg);
        }

        //{"found" : true, "person": "any"}

        if (msg.found) {
            $('div.main').show(1000);

            var newDateObj = new Date(new Date().getTime() + hideInterval);

            hideTime = newDateObj;

            if (msg.person == "any") { // unknown person

            } else { // known person
                //TODO
            }

            setTimeout(hideEverything, hideInterval);
        }
    });
}

// ############ Carousel #############

function scroll(){
  console.log('scroll!');
  $('.jcarousel').jcarousel('scroll', '+=1');
  setTimeout(scroll, scrollInterval);
}

function initCarousel(){
  var jcarousel = $('.jcarousel');
  jcarousel.jcarousel({
          wrap: 'circular',
          vertical: true
      })
  scroll();
}

function resetCarousel(){
  $('.jcarousel').jcarousel('reload');
}

(function($) {
    $(function() {
        initCarousel()
    });
})(jQuery);

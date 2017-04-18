function main(socket) {
            console.log("adding weather-forecast-module");

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
                        url: "./html/weather-forecast-modul.html",
                        success: function(result) {

                            result = result.replace("###1###", loc).replace("###2###", loc);

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
          }

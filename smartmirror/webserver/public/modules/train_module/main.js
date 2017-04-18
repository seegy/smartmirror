function main (socket) {
    console.log("adding train-module");

    socket.on('train-news', function(msg) {
        if (msg !== null && typeof msg !== 'object') {
            msg = JSON.parse(msg);
        }

        var mod = $("div[type='trains'][from='" + msg.from + "'][to='" + msg.to + "']");

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
                mod.find(e).empty();
                mod.find(e).append(newContent[i]);
            });
            resetCarousel();
        }


        if (mod[0] === undefined) {
            console.log('module unknown for trains: ' + msg.from + ',' + msg.to);

            $.ajax({
                url: "./modules/train_module/view.html",
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
}

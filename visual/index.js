/*
 * author: winton
 */

(function($) {
    $.getChartsInfo = function() {
        var url = window.location.search;
        var args = {};
        if (url.indexOf('?') != -1) {
            var str = url.substr(1);
            var arglist = str.split('&');
            for (var i in arglist) {
                argstr = arglist[i];
                if (argstr != null & argstr != '') {
                    var key = argstr.split('=')[0];
                    var value = argstr.split('=')[1];
                    if (key == 'data') {
                        if (args[key] == undefined) {args[key] = []}
                        args[key].push(unescape(value));
                    } else {
                        args[key] = unescape(value);
                    }
                }
            }
        }
        return args;
    };
})(jQuery);

function renderData(stat) {
    Visual.createChart(stat, $('.charts-view'));
}

$(document).ready(function() {
    var chart = $.getChartsInfo();

    statgroup = [];
    for (var i in chart.data) {
        statpath = chart.data[i];
        $.ajax({
            url: '/stat/' + statpath,
            dataType: 'json',
            async: false,
            success: function(data) {
                statgroup.push(data);
            }
        });
    }
    if (statgroup.length == 0) {
        console.warn('cannot get data');
        $('.charts-view').text('无法获取到相关数据');
        return;
    }
    var data = {
        type: statgroup[0].type,
        visualization: statgroup[0].visualization,
        statgroup: statgroup,
    };
    if (chart.v != undefined) {
        data.visualization = chart.v;
    }
    renderData(data);
});

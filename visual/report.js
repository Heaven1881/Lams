
String.prototype.replaceInFormat = function(repl) {
    return this.replace(/\{(\w+)\}/g, function(match, capture) {
        return repl[capture];
    });
};

function paserData($el) {
    var chart = {};
    chart.visualization = $el.data('v');
    chart.height = $el.data('height');
    if (chart.height == null) chart.height = '400px';
    chart.width = $el.data('width');
    if (chart.width == null) chart.width = '900px';

    chart.data = [];
    $el.find('data').each(function() {
        chart.data.push($(this).text());
    });
    return chart;
}

function loadChartStat(chart) {
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
        return null;
    }
    var data = {
        type: statgroup[0].type,
        visualization: chart.visualization,
        statgroup: statgroup,
    };
    return data;
}

$(function() {
    $('chart').each(function() {
        var chart = paserData($(this));
        var data = loadChartStat(chart);
        if (data != null) {
            var $view = $('<div class="charts-view"></div>').appendTo($(this));
            $view.css('height', chart.height);
            $view.css('width', chart.width);
            Visual.createChart(data, $view);
        }
    });
});


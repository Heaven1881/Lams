/*
 * HightCharts库的调用函数
 */

var Visual = {};

Visual.createChart = function (stat, $view) {
    var visualization = stat.visualization;
    var visualMethod = Visual.visualMethodDef[visualization];
    if (visualMethod == undefined) {
        console.warn('Cannot find visualMethod for "', visualization, '"');
    } else {
        visualMethod(stat, $view);
    }
};

Visual._getCountStatValue = function(key, jsonlist, defaultValue) {
    for (var i in jsonlist) {
        var jsonitem = jsonlist[i];
        if (jsonitem.name == key) {
            return jsonitem.y;
        }
    }
    return defaultValue;
}

/*
 * 定义可视化描述和其对应的可视化方法
 */
Visual.visualMethodDef = {};

Visual.visualMethodDef['pie'] = function(stat, $view) {
    //TODO pie 只能处理一个系列的数据
    stat = stat.statgroup[0];

    if (stat.type != 'CountStat') {
        console.warn('"', stat.type, '"', 'cannot be visualiazed by "', 'pie', '"');
        return;
    }

    $view.highcharts({
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false
        },
        title: {
            text: stat.title
        },
        tooltip: {
            pointFormat: '{series.name}: <b>{point.y}</b>'
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: true,
                    color: '#000000',
                    connectorColor: '#000000',
                    format: '<b>{point.name}</b>: {point.percentage:.1f} %'
                }
            }
        },
        series: [{
            type: 'pie',
            name: '人数',
            data: stat.stat,
        }]
    });
};

Visual.visualMethodDef['heatmap'] = function(stat, $view) {
    // TODO heatmap 只能处理一个系列的数据
    stat = stat.statgroup[0];

    if (stat.type != 'HeatmapStat') {
        console.warn('"', stat.type, '"', 'cannot be visualiazed by "', 'heatmap', '"');
        return;
    }

    csvStr = '';
    for (var i in stat.stat) {
        item = stat.stat[i];
        csvStr += item.join(',') + '\n';
    }
    $view.highcharts({
        data: {
            csv: csvStr,
        },
        chart: {
            type: 'heatmap',
        },
        title: {
            text: stat.title,
            align: 'left'
        },
        xAxis: {
            tickPixelInterval: 50,
            min: Date.parse(new Date) - 3600 * 1000 * 24 * 100, // 过去100天
            max: Date.parse(new Date) + 3600 * 1000 * 24, //当前日期的下一天
        },
        yAxis: {
            title: {
                text: null
            },
            labels: {
                format: '{value}:00'
            },
            minPadding: 0,
            maxPadding: 0,
            startOnTick: false,
            endOnTick: false,
            tickPositions: [0, 6, 12, 18, 24],
            tickWidth: 1,
            min: 0,
            max: 23
        },

        colorAxis: {
            minColor: '#EEE685',
            maxColor: '#B22222'
        },

        series: [{
            borderWidth: 0,
            colsize: 24 * 36e5, // one day
            tooltip: {
                headerFormat: '',
                pointFormat: '{point.x:%Y-%m-%d} {point.y}:00 答题人次:{point.value}'
            }
        }]

    });
};

Visual.visualMethodDef['polar'] = function(stat, $view) {
    if (stat.type != 'CountStat') {
        console.warn('"', stat.type, '"', 'cannot be visualiazed by "', 'polar', '"');
        return;
    }

    // 将数据转换为规定的格式
    var categories = [];
    var series = [];
    var title = '';
    for (var i in stat.statgroup) {
        title += stat.statgroup[i].title + ' ';
        series.push({
            name: stat.statgroup[i].title,
            data: [],
            pointPlacement: 'on',
        });
        stat.statgroup[i]
        var statdata = stat.statgroup[i].stat;
        for (var j in statdata) {
            if(categories.indexOf(statdata[j].name) == -1) {
                categories.push(statdata[j].name);
            }
        }
    }
    for (var i in categories) {
        cate = categories[i];
        for (var j in series) {
            var count = Visual._getCountStatValue(cate, stat.statgroup[j].stat, 0);
            series[j].data.push(count);
        }
    }
    console.info(series)

    // 绘图
    $view.highcharts({
        chart: {polar: true, type: 'line'},
        title: {text: title, x: -80},
        pane: {size: '80%'},
        xAxis: {
            categories: categories,
            tickmarkPlacement: 'on',
            lineWidth: 0
        },
        yAxis: {gridLineInterpolation: 'polygon', lineWidth: 0, min: 0},
        tooltip: {
            shared: true,
            pointFormat: '<span style="color:{series.color}">{series.name}: <b>{point.y}</b><br/>'
        },
        legend: {align: 'right', verticalAlign: 'top', y: 70, layout: 'vertical'},
        series: series,
    });
};


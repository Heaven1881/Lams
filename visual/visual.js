/*
 * HightCharts库的调用函数
 */

var Visual = {};
Visual.Default = {};    // 默认方法
Visual.visualMethodDef = {}; //保存特定的方法

/*
 * 默认的配置
 */
Visual.Default.plotOptions = {
    bar: {
        dataLabels: {enabled: true}
    },
    column: {
        pointPadding: 0.2,
        borderWidth: 0
    },
    area: {
        marker: {
            enabled: false,
            symbol: 'circle',
            radius: 2,
            states: { hover: { enabled: true } }
        }
    },
    areaspline: {
        marker: {
            enabled: false,
            symbol: 'circle',
            radius: 2,
            states: { hover: { enabled: true } }
        }
    },
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
};

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

Visual.parseCountStat = function(stat) {
    var xName = [];
    var series = [];
    var title = '';
    var xTitle = null;
    var yTitle = null;
    var legendenabled = true;

    for (var i in stat.statgroup) {
        title += stat.statgroup[i].title + ' ';
        series.push({
            name: stat.statgroup[i].title,
            data: [],
        });
        var statdata = stat.statgroup[i].stat;
        for (var j in statdata) {
            if (xName.indexOf(statdata[j].name) == -1) {
                xName.push(statdata[j].name);
            }
        }
    }
    for (var i in xName) {
        var name = xName[i];
        for (var j in series) {
            var count = Visual._getCountStatValue(name, stat.statgroup[j].stat, 0);
            series[j].data.push(count);
        }
    }

    if (stat.statgroup.length > 1) title = null;
    if (stat.statgroup[0].xTitle != null) xTitle = stat.statgroup[0].xTitle;
    if (stat.statgroup[0].yTitle != null) yTitle = stat.statgroup[0].yTitle;
    if (stat.statgroup.length == 1) legendenabled = false;

    return {
        name: xName,
        series: series,
        title: title,
        xTitle: xTitle,
        yTitle: yTitle,
        legendenabled: legendenabled,
    };
}

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
            pointFormat: '<b>{point.y}</b>'
        },
        plotOptions: Visual.Default.plotOptions,
        series: [{
            type: 'pie',
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
    stat = Visual.parseCountStat(stat);
    var categories = stat.name;
    var series = stat.series;
    var title = stat.title;

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
        yAxis: {gridLineInterpolation: 'polygon', lineWidth: 0, min: 0, max: 1},
        tooltip: {
            shared: true,
            headerFormat: '',
            pointFormat: '<span style="color:{series.color}">{series.name}: <b>{point.y}</b><br/>'
        },
        legend: {align: 'right', verticalAlign: 'top', y: 70, layout: 'vertical'},
        series: series,
    });
};

Visual.visualMethodDef['areaspline'] = function(stat, $view) {
    if (stat.type != 'CountStat') {
        console.warn('"', stat.type, '"', 'cannot be visualiazed by "', 'areaspline', '"');
        return;
    }
    Visual.Default.CountStatVisualFunc(stat, $view, 'areaspline');
};

Visual.visualMethodDef['area'] = function(stat, $view) {
    if (stat.type != 'CountStat') {
        console.warn('"', stat.type, '"', 'cannot be visualiazed by "', 'area', '"');
        return;
    }
    Visual.Default.CountStatVisualFunc(stat, $view, 'area');
};

Visual.visualMethodDef['line'] = function(stat, $view) {
    if (stat.type != 'CountStat') {
        console.warn('"', stat.type, '"', 'cannot be visualiazed by "', 'line', '"');
        return;
    }
    Visual.Default.CountStatVisualFunc(stat, $view, 'line');
};

Visual.visualMethodDef['spline'] = function(stat, $view) {
    if (stat.type != 'CountStat') {
        console.warn('"', stat.type, '"', 'cannot be visualiazed by "', 'spline', '"');
        return;
    }
    Visual.Default.CountStatVisualFunc(stat, $view, 'spline');
};

Visual.visualMethodDef['column'] = function(stat, $view) {
    if (stat.type != 'CountStat') {
        console.warn('"', stat.type, '"', 'cannot be visualiazed by "', 'column', '"');
        return;
    }
    Visual.Default.CountStatVisualFunc(stat, $view, 'column');
};

Visual.visualMethodDef['bar'] = function(stat, $view) {
    if (stat.type != 'CountStat') {
        console.warn('"', stat.type, '"', 'cannot be visualiazed by "', 'bar', '"');
        return;
    }
    Visual.Default.CountStatVisualFunc(stat, $view, 'bar');
};

/*
 * 默认的渲染方式
 */
Visual.Default.CountStatVisualFunc = function(stat, $view, type) {
    stat = Visual.parseCountStat(stat);
    var xName = stat.name

    // 绘图
    $view.highcharts({
        chart: {
            type: type,
        },
        title: { text: stat.title },
        xAxis: {
            title: {text: stat.xTitle, align: 'high'},
            labels: {
                formatter: function() {
                    return xName[this.value];
                }
            }
        },
        yAxis: { title: {text: stat.yTitle, align: 'middle'}},
        tooltip: {
            formatter: function() {
                return stat.xTitle + ':' + xName[this.point.x] + '<br>' + stat.yTitle + ':' + this.y;
            }
        },
        plotOptions: Visual.Default.plotOptions,
        series: stat.series,
        legend: {enabled: stat.legendenabled},
    });
}

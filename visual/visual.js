/*
 * HightCharts库的调用函数
 */

var Visual = {};

Visual.createChart = function (stat, $view) {
    var type = stat.type;
    var visualMethod = Visual.visualMethodDef[type];
    if (visualMethod == undefined) {
        console.warn('Cannot find visualMethod for "', type, '"');
    } else {
        visualMethod(stat, $view);
    }
};


/*
 * 定义可视化描述和其对应的可视化方法
 */
Visual.visualMethodDef = {};

Visual.visualMethodDef['CountStat'] = function(stat, $view) {
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

Visual.visualMethodDef['HeatmapStat'] = function(stat, $view) {
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
                pointFormat: '{point.x:%e %b, %Y} {point.y}:00 答题人次:{point.value}'
            }
        }]

    });
};


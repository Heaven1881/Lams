/*
 * D3库的调用函数
 */

var Visual = {};

Visual.createChart = function (stat, $view) {
    var visualization = stat.visualization;
    var visualMethod = Visual.visualMethodDef[visualization];
    if (visualMethod == undefined) {
        console.warning('Cannot find visualMethod for "', visualization, '"');
    } else {
        console.info('find method');
    }
};


/*
 * 定义可视化描述和其对应的可视化方法
 */
Visual.visualMethodDef = {};

Visual.visualMethodDef['pie-chart'] = function(stat, view) {

};

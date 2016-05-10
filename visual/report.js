
String.prototype.replaceInFormat = function(repl) {
    return this.replace(/\{(\w+)\}/g, function(match, capture) {
        return repl[capture];
    });
};

var Report = {}

// 记录当前激活的render
Report._render = []

// 记录各个render的处理函数
Report._renderFunc = {}

// 记录当前Report使用到的json数据
Report._data = {}

// 从url同步获取数据, 有缓存机制, url可以是list
Report.syncLoad = function(urlList) {
    if (typeof urlList == 'string')
        urlList = [urlList];

    var dataList = [];
    for (var i in urlList) {
        var url = urlList[i];
        var data = undefined;
        if (url in Report._data) {
            data = Report._data[url];
        } else {
            $.ajax({
                url: '/stat/' + url,
                dataType: 'json',
                async: false,
                success: function(res) {
                    data = res;
                },
            });
            Report._data[url] = data;
        }
        dataList.push(data);
    }
    return dataList;
};

// 注册render
Report.registerRender = function(renderSet) {
    $.extend(Report._renderFunc, renderSet);
    for (var key in renderSet) {
        Report._render.push(key);
    }
};

// report 初始化函数，所有report渲染的入口
Report.init = function(student) {
    for (var i in Report._render) {
        var renderName = Report._render[i];
        var renderFunc = Report._renderFunc[renderName];
        $(renderName).each(function() {
            try {
                var $el = $(this);
                var urlList = [];
                $el.find('data').each(function() {
                    preUrl = $(this).text()
                    urlList.push(preUrl.replaceInFormat(student));
                });
                var datalist = Report.syncLoad(urlList);
                renderFunc($el, $el.data(), datalist);
            } catch (err) {
                console.warn(err);
            }
        });
    }
};

$(function() {
    var email = 'maye9999@163.com';
    $.ajax({
        url: '/stat/data.info/' + email + '.json',
        dataType: 'json',
        success: function(res) {
            res.piazzaEmail = res.edxEmail;
            Report.init(res);
        }
    });
});

// 内置Render
// 处理chart标签
Report.registerRender({'lams-chart': function($el, attr, datalist) {
    if (datalist.length == 0) {
        console.warn('no data!');
        return;
    }

    var data = {
        type: datalist[0].type,
        visualization: attr.v || datalist[0].visualization,
        statgroup: datalist,
    };
    var $view = $('<div class="charts-view"></div>');
    $el.after($view);
    $view.css('height', attr.height);
    $view.css('width', attr.width);
    Visual.createChart(data, $view);
}});

// 内置Render
// 使用handlebars处理lams-hb标签
Report.registerRender({'lams-hb': function($el, attr, datalist) {
    var source = $el.find('script[type="text/x-handlebars-template"]').html();
    var template = Handlebars.compile(source);

    var data = {'nodata': true};
    var alpha = ['a', 'b', 'c', 'd', 'e', 'f', 'g'];
    if (datalist.length == 1) {
        data = datalist[0];
    } else if (datalist.length > 1) {
        for (var i in datalist) {
            data[alpha[i]] = datalist[i];
        }
    }
    var html = template(data);
    var $view = $('<div class="hb-view"></div>');
    $el.after($view);
    $view.html(html);
}});

// each:按章节顺序升序处理
Handlebars.registerHelper('each_section', function(array, opts) {
    array = array.sort(function(a, b) {
        var a = parseInt(a['name'].split('-')[1] || 99);
        var b = parseInt(b['name'].split('-')[1] || 99);
        if (a > b) return 1;
        if (a < b) return -1;
        if (a == b) return 0;
    });

    var result = '';
    for (var i in array) {
        result += opts.fn(array[i]);
    }
    return result;
});


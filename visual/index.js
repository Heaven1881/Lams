/*
 * author: winton
 */

(function($) {
    $.getStatData = function() {
        var reg = new RegExp('^/view/(.+.json)$');
        var r = window.location.pathname.match(reg);
        return unescape(r[1]);
    };
})(jQuery);

function renderData(stat) {
    console.info(stat);
    Visual.createChart(stat, $('body'));
}

$(document).ready(function() {
    var statpath = $.getStatData();
    if (statpath == null) {
        console.warning('cannot get statpath');
    }
    $.ajax({
        url: '/stat/' + statpath,
        dataType: 'json',
        success: renderData,
    });
});

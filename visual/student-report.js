Handlebars.registerHelper('Compare', function(sectionName, score, allSection) {
    var gradeList = allSection.res[sectionName];
    var answeredStu = gradeList.length;
    var betterStu = 0;
    for (var i in gradeList) {
        var grade = gradeList[i];
        if (grade > score) {
            betterStu += 1;
        }
    }
    return answeredStu + '人答题，有' + betterStu + '人得分更高';
});

function getQueryString(name) {
    var reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)', 'i');
    var r = window.location.search.substr(1).match(reg);
    if (r != null) return unescape(r[2]); return null;
}

$(function() {
    var email = getQueryString('email');
    $.ajax({
        url: '/stat/data.info/' + email + '.json',
        dataType: 'json',
        success: function(res) {
            res.piazzaEmail = res.edxEmail;
            Report.init(res);
        },
        error: function() {
            Report.init({edxEmail: email});
        }
    });
});

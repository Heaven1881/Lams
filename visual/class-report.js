Handlebars.registerHelper('Average', function(totalScore, student, complete) {
    //return new Handlebars.SafeString(converter.makeHtml(text));
    var avg = (totalScore / student).toFixed(2);
    var avgMax = (totalScore / student / complete).toFixed(0);
    return avg + '/' + avgMax;
});

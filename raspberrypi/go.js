var express = require('express');
var app = express();

app.get('/start', function (req, res) {
    res.send('Party Started!');
    var python = require('child_process').spawn(
        'python',
        ["/home/pi/nye/partybutton/partybutton.py"])
    console.log('Party Started!')
});

var server = app.listen(3000, function () {
    var host = server.address().address;
    var port = server.address().port;

    console.log('Example app listening at http://%s:%s', host, port);
});
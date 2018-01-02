var http = require('http');
var url = require('url');
var mysql = require('mysql');

var connection = mysql.createConnection({
    port     : process.env.SEVEN_SERVICE_MYSQL_PORT,
    host     : process.env.SEVEN_SERVICE_PROXY_HOST,
    user     : 'admin',
    password : 'mypassword'
});

console.log('Found port as: ' + process.env.SEVEN_SERVICE_MYSQL_PORT)

http.createServer(function (req, res) {
  reqUrl = url.parse(req.url, true);

  res.useChunkedEncodingByDefault = false;
  res.writeHead(200, {'Content-Type': 'text/html'});

  if (reqUrl.pathname == '/_ah/health') {
    res.end('ok');
  } else if (reqUrl.pathname == '/exit') {
    process.exit(-1)
  } else {
      connection.query('use demo;', function(err) {
          if (err) {
              res.end('error: ' + err);
              connection.end();
          } else {
              if (reqUrl.query && reqUrl.query['msg']) {
                  var msg = reqUrl.query['msg'];
                  connection.query('insert into log(message) values (' + connection.escape(msg) + ');', function(err) {
                      if (err) {
                          res.end('error: ' + err);
                      } else {
                          res.end('added');
                      }
                 });
              } else {
                  connection.query('select * from log;', function(err, rows, fields) {
                      if (err) {
                      res.end('error: ' + err);
                      } else {
                          var result = '';
                          for (var i = 0; i < rows.length; ++i) {
                              result += rows[i].message + '<br>';
                          }
                          res.end(result);
                      }
                  });
              }
          }
      })
  }

}).listen(8080, '0.0.0.0');

console.log('Server running at http://127.0.0.1:8080/');

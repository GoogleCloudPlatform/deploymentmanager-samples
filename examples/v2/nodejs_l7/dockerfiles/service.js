var http = require('http');
var url = require('url');

console.log('Started static node server')

http.createServer(function (req, res) {
  reqUrl = url.parse(req.url, true);

  res.useChunkedEncodingByDefault = false;
  res.writeHead(200, {'Content-Type': 'text/html'});

  if (reqUrl.pathname == '/_ah/health') {
    res.end('ok');
  } else if (reqUrl.pathname == '/exit') {
    process.exit(-1)
  } else {
      res.end('static server');
  }
}).listen(8080, '0.0.0.0');

console.log('Static server running at http://127.0.0.1:8080/');

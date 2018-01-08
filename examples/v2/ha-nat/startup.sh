#!/bin/bash
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

cat <<EOF > /usr/local/sbin/health-check-server.py
#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import subprocess

PORT_NUMBER = 80
PING_HOST = "www.google.com"

def connectivityCheck():
  try:
    subprocess.check_call(["ping", "-c", "1", PING_HOST])
    return True
  except subprocess.CalledProcessError as e:
    return False

#This class will handle any incoming request
class myHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    if self.path == '/health-check':
      if connectivityCheck():
        self.send_response(200)
      else:
        self.send_response(503)
    else:
      self.send_response(404)


try:
  server = HTTPServer(("", PORT_NUMBER), myHandler)
  print "Started httpserver on port " , PORT_NUMBER
  #Wait forever for incoming http requests
  server.serve_forever()

except KeyboardInterrupt:
  print "^C received, shutting down the web server"
  server.socket.close()
EOF

nohup python /usr/local/sbin/health-check-server.py >/dev/null 2>&1 &

# Copyright 2018 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Healthz server invoked from startup script invoked on GCE instance."""

import BaseHTTPServer
import getopt
import logging
import ssl
import sys
import urlparse


class HealthzHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  """Handler for HTTP requests."""

  health_status = 'HEALTHY'

  def do_GET(self):  # pylint: disable=C0103
    """Handler for GET requests."""
    parsed_path = urlparse.urlparse(self.path)
    response_code = 400
    if parsed_path.path == '/change_status':
      HealthzHandler.health_status = parsed_path.query
      print 'changed health status to ' + HealthzHandler.health_status
      response_code = 200
    elif parsed_path.path == '/healthz':
      if HealthzHandler.health_status == 'HEALTHY':
        response_code = 200
      elif HealthzHandler.health_status == 'UNHEALTHY':
        response_code = 500
    self.send_response(response_code)
    self.send_header('Content-type', 'text/html')
    self.end_headers()
    self.wfile.write(HealthzHandler.health_status)


def main():
  # Process flags
  port = 12345
  cert_file = ''
  key_file = ''
  try:
    opts, _ = getopt.getopt(
        sys.argv[1:],
        '',
        ['port=', 'cert_file=', 'key_file='])
  except getopt.GetoptError:
    logging.error(
        'healthz_server.py '
        '--port <port> --cert_file <cert_file> --key_file <key_file>')
    sys.exit(2)
  for opt, arg in opts:
    if opt == '--port':
      port = int(arg)
    elif opt == '--cert_file':
      cert_file = arg
    elif opt == '--key_file':
      key_file = arg

  # Start server
  healthz_server = BaseHTTPServer.HTTPServer(('', port), HealthzHandler)
  print 'Started healthz_server on port', port
  if cert_file and key_file:
    healthz_server.socket = ssl.wrap_socket(
        healthz_server.socket,
        certfile=cert_file,
        keyfile=key_file,
        server_side=True)
  healthz_server.serve_forever()


if __name__ == '__main__':
  main()

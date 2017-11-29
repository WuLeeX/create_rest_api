#!/usr/bin/python

import json
from http.server import BaseHTTPRequestHandler,HTTPServer

class AlarmHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # self.send
        self.send_response(200, 'OK')
        self.end_headers()
        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        if "alerts" in data:
            text = "%s %s" % (data["alerts"][0]["annotations"], data["status"])
        else:
            text = {}
        print(text)
        resp = text

    def do_GET(self):
        self.protocal_version = "HTTP/1.1"
        self.send_response(200)
        self.send_header("Welcome", "Contect")
        self.end_headers()
        self.wfile.write('well done')
        # print(json.dumps(resp))

if __name__ == '__main__':
   httpd = HTTPServer(('10.9.11.95',1234), AlarmHandler)
   httpd.serve_forever()
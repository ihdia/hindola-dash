
from SimpleHTTPServer import SimpleHTTPRequestHandler, BaseHTTPServer

def run(server_class=BaseHTTPServer.HTTPServer,
        handler_class=BaseHTTPServer.BaseHTTPRequestHandler):
    server_address = ('10.5.0.142', 8000)
    self.send_header('Access-Control-Allow-Origin', '*')
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

 

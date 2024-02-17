# pong.py
from http.server import BaseHTTPRequestHandler, HTTPServer

class PongServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Pong!")

if __name__ == "__main__":
    server_address = ('', 80)
    httpd = HTTPServer(server_address, PongServer)
    print("Starting pong server...")
    httpd.serve_forever()

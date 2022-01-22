from datetime import datetime
import sys
import http.server

HOST = "localhost"
PORT = 8000

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):

        if self.path.endswith("with_cache.html"):
            self.send_header("Cache-Control", "max-age=10")
        elif self.path.endswith("without_cache.html"):
            self.send_header("Cache-Control", "no-store")
        else:
            raise Exception("No such resource on this server")


        http.server.SimpleHTTPRequestHandler.do_GET(self)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        PORT = int(sys.argv[1])

    server = http.server.HTTPServer((HOST, PORT), ProxyHandler)

    try:
        server.serve_forever()
        print("started server http://%s:%s" % (HOST, PORT))
    except KeyboardInterrupt:
        server.server_close()
        print("shutdown server")

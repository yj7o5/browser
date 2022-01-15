from http import server
from datetime import datetime
import sys

class CacheHandler(server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print(self.path)

        self.send_header("Cache-Content", "max-age=60")

        server.SimpleHTTPRequestHandler.do_GET(self)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("port is required")

    port_number = int(sys.argv[1])
    server.test(HandlerClass=CacheHandler, port=port_number)

    print("listening on http://*:{}".format(port_number))

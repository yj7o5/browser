from datetime import datetime
import sys
import http.server
import time

HOST = "localhost"
PORT = 8000

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        load_file = ""
        cache_value = ""

        if self.path.endswith("with_cache.html"):
            load_file = "./with_cache.html"
            cache_value = "max-age=10"
        elif self.path.endswith("without_cache.html"):
            load_file = "./without_cache.html"
            cache_value = "no-store"
        else:
            http.server.SimpleHTTPRequestHandler.do_GET(self)

        if load_file:
            self.send_response(200)
            self.send_header("Cache-Control", cache_value)
            self.send_header("Content-Type", "text/html")

            # simulate latency when loading page to allow for testing loading from browser cache
            time.sleep(10)

            with open(load_file, "r") as f:
                content = f.read().encode("utf-8")
                self.send_header("Content-Length", len(content))
                self.end_headers()
                self.wfile.write(content)



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

import ssl
import socket
import gzip
import io
from urllib.parse import urlparse

"""
SCHEME HANDLERS
"""
def handle_http(scheme, host, path, only_view_source = False):
    r = None
    # init ipv4 basic tcp stream socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP) as s:

        # wrap socket with ssl context, if https scheme given
        if scheme.startswith("https"):
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=host)

        # connect to the resolve host/port
        s.connect(resolve_host_port(scheme, host))

        # prepare raw http request
        s.send(create_request(host, path))
        r = s.makefile("rb", newline="\r\n")

    # parse response status
    status_line = r.readline().decode()
    status_code = int(status_line.split(" ", 2)[1])
    assert(status_code >= 200 and status_code < 400)

    # parse response headers
    headers = parse_headers(r)

    # check for redirection: (TODO: check for infinite loop)
    if status_code >= 300 and status_code < 400:
        loc = headers["location"]
        # same host and scheme as the original request being used
        if loc.startswith("/"):
            handle_http(r.scheme, r.netloc, r.path)
        else:
        # otherwise extract the locations parts
            r = urlparse(headers["location"])
            handle_http(r.scheme, r.netloc, r.path)
        return

    # init the body to captured from network stream
    body = b""

    # read as usual if no transfer encoding is needed
    if "chunked" != headers.get("transfer-encoding"):
        body = r.read()
    else:
        # decode chunks as per the specs laid out here:
        # source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Transfer-Encoding#chunked_encoding
        i = 0
        chunks = r.read().split(b"\r\n")
        for chunk in chunks:
            if len(chunk) > 0 and i % 2 == 1:
                body += chunk
            i += 1

    # decompress if gzip encoding enabled:
    if "gzip" == headers.get("content-encoding"):
        body = gzip.decompress(body)

    body = body.decode()

    if only_view_source:
        print(body)
    else:
        show_html(body)

def handle_file(scheme, path):
    r = None
    if path == None or path == "":
        path = "/var/log/daily.out" # default to random file

    # create UNIX local filesystem socket
    with open(path, "r") as s:
        r = s.read()
    print(r)

def handle_data(scheme, path):
    _, content = path.split(",", 1)

    # assume we'll always have html content type, otherwise check if
    show_inline_html(content)

"""
UTILITY METHODS
"""
def parse_headers(response):
    h = {}
    while True:
        line = response.readline().decode()

        # exit out as line breaks marks the end of h
        if line == "\r\n": break
        header, value = line.split(":", 1)
        h[header.lower()] = value.strip()

    return h

def add_request_header(r, header, value):
    r += "{}: {}\r\n".format(header, value)
    return r

def create_request(host, path):
    r = "GET {} HTTP/1.1\r\n".format(path)
    r = add_request_header(r, "Host", host)
    r = add_request_header(r, "Connection", "close")
    r = add_request_header(r, "User-Agent", "python-browser")
    r = add_request_header(r, "Accept-Encoding", "gzip")

    return (r + "\r\n").encode()

def resolve_host_port(scheme, host):
    # configure the appropriate port
    port = 80 if scheme == "http" else 443

    # reset port, if custom port is specified in the url
    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)

    return host, port

def show_inline_html(content):
    inside_tag = False
    for c in content:
        if c == '<':
            inside_tag = True
        elif c == '>':
            inside_tag = False
        elif not inside_tag:
            print(c, end='')

def show_html(html):
    html_len = len(html)

    def scan_tag(reader, idx):
        tag = ""
        if reader[idx] == '<':
            idx += 1
        else:
            return tag, idx

        while (idx < html_len and reader[idx] != '>'):
            if reader[idx] != '/':
                tag += reader[idx]
            idx += 1

        return tag, idx

    def scan_entities(reader, idx):
        key = ""
        entities = {"lt": "<", "gt": ">", "amp": "&"}

        if reader[idx] != '&':
            return None, idx

        idx += 1
        while idx < len(reader) and reader[idx] != ';':
            key += reader[idx]
            idx += 1

        if key in entities:
            return entities[key], idx

        return None, idx

    i = 0
    inside_body = False
    while i < html_len:
        tag, idx = scan_tag(html, i)
        i = idx
        if tag == "body":
            inside_body = not inside_body
        elif inside_body and tag == "":
            entity, idx = scan_entities(html, i)
            i = idx

            if entity:
                print(entity, end='')
            else:
                print(html[i], end='')

        i += 1

"""
MAIN FUNCTIONS
"""
def request(url):
    scheme, host, path, _, _, _ = urlparse(url)

    if scheme.startswith("http"):
        handle_http(scheme, host, path)
    elif scheme.startswith("file"):
        handle_file(scheme, path)
    elif scheme.startswith("data"):
        handle_data(scheme, path)
    elif scheme.startswith("view-source"):
        r = urlparse(path) # since "path" carries the URL info
        handle_http(r.scheme, r.netloc, r.path, True)
    else:
        raise Exception("cannot handle scheme {}".format(scheme))

if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else ""
    request(url)

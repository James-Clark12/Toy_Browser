import socket
import ssl


def request(url):

    # check the url starts with http or https - assert throws error otherwise
    scheme, url = url.split("://", 1)
    assert scheme in ["http", "https"], \
        "Unknown scheme {}".format(scheme)
    # assume a port - but can be corrected later if custom port exists
    port = 80 if scheme == "http" else 443

    # split the remainder into host and path, path is everything coming after / - e.g. example.org/index.html
    # split takes two paremters - the first is what to split on, the second is called maxsplit -
    # it asks how many splits to do - defaults to -1 which means as many as instances of the character that exist
    host, path = url.split("/", 1)
    path = "/" + path

    # here we check for a custom port
    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)

    print('host ', host)
    print('port ', port)
    print('path ', path)

    # we now want to connect to the host
    # for that we need a socket
    s = socket.socket(
        family=socket.AF_INET,  # address family - how we find the other computer
        # type - what sort of conversation we're having - stream means we can send arbitrary amounts of data
        type=socket.SOCK_STREAM,
        proto=socket.IPPROTO_TCP,  # protocol - we are using TCP
    )
    # if the connect is https we need to encrypt our socket with TLS
    if scheme == "https":
        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(s, server_hostname=host)

    # we connect to the host at the determined port
    # connect takes a single argument, and that argument is a pair of a host and a port. This is because different address families have different numbers of arguments.
    s.connect((host, port))
    s.send("GET {} HTTP/1.0\r\n".format(path).encode("utf8") +
           "Host: {}\r\n\r\n".format(host).encode("utf8"))

    # we save the message we received in response
    response = s.makefile("r", encoding="utf8", newline="\r\n")

    # now we can parse the message
    statusline = response.readline()
    version, status, explanation = statusline.split(" ", 2)
    assert status == "200", "{}: {}".format(status, explanation)

    headers = {}
    while True:
        line = response.readline()
        if line == "\r\n":
            break
        header, value = line.split(":", 1)
        headers[header.lower()] = value.strip()

    assert "transfer-encoding" not in headers
    assert "content-encoding" not in headers

    body = response.read()
    s.close()
    return headers, body


def show(body):
    in_angle = False
    for c in body:
        if c == "<":
            in_angle = True
        elif c == ">":
            in_angle = False
        elif not in_angle:
            print(c, end="")


def printHeaders(headers):
    for header, value in headers.items():
        print(header, ": ", value)


def load(url):
    print("Running browser.py", "", "\r\n")
    headers, body = request(url)
    # printHeaders(headers)
    show(body)


# url = "http://example.org/index.html"
# load(url)

if __name__ == "__main__":
    import sys
    load(sys.argv[1])

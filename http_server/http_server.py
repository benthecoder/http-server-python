import socket
import threading  # multiple connections
import argparse
import os

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 4221  # Port to listen on (non-privileged ports are > 1023)


class HTTPResponse:
    """Constructs an HTTP response object with a status code, body, and headers.

    Args:
        status_code (int): HTTP response status code.
        body (bytes, optional): Response body in bytes. Defaults to None.
        headers (dict, optional): Response headers in a dictionary. Defaults to None.
    """

    def __init__(self, status_code: int, body: bytes = None, headers: dict = None):
        self.status_code = status_code
        self.body = body
        self.headers = headers or {}

    @property
    def status_line(self):
        return f"HTTP/1.1 {self.status_code}"

    @property
    def headers_section(self):
        return "\r\n".join(
            f"{k}: {v}"
            for k, v in {
                "Content-Length": len(self.body) if self.body else 0,
                **self.headers,
            }.items()
        )

    def __bytes__(self):
        return f"{self.status_line}\r\n{self.headers_section}\r\n\r\n".encode(
            "utf-8"
        ) + (self.body or b"")


class HTTPRequest:
    """Representation of an HTTP request received by the server.

    This class can parse details from a raw HTTP request,
    including the headers, body, status line (method, path, protocol), etc.

    Args:
        raw_contents (bytes): The raw bytes of the HTTP request.
    """

    raw_contents: bytes

    def __init__(self, raw_contents: bytes):
        self.raw_contents = raw_contents

    @property
    def headers_section(self):
        return b"\r\n".join(self.raw_contents.split(b"\r\n")[1:])

    @property
    def headers(self):
        return dict(
            [item.decode("utf-8") for item in line.split(b": ")]
            for line in self.headers_section.split(b"\r\n")
            if line
        )

    @property
    def body(self):
        return self.raw_contents.split(b"\r\n\r\n")[1]

    @property
    def status_line(self):
        return self.raw_contents.split(b"\r\n")[0]

    @property
    def method(self):
        return self.status_line.split(b" ")[0].decode("utf-8")

    @property
    def path(self):
        return self.status_line.split(b" ")[1].decode("utf-8")

    @property
    def protocol(self):
        return self.status_line.split(b" ")[2].decode("utf-8")

    def __repr__(self):
        return f"<HTTPRequest {self.method} {self.path}>"


def handle_connection(conn, data_directory):
    """Handles individual client connections and HTTP requests.

    Accepts a connection object and the data directory to function. Parses
    the client request, interprets the HTTP method, and communicates with the file system or echoes back the client

    """
    req = conn.recv(1024)
    request = HTTPRequest(req)

    if request.path == "/":
        conn.sendall(bytes(HTTPResponse(200)))
    elif request.path.startswith("/echo"):
        value = request.path.split("/echo/")[1]
        response = HTTPResponse(
            200, body=value.encode("utf-8"), headers={"Content-Type": "text/plain"}
        )
        conn.sendall(bytes(response))
    elif request.path == "/user-agent":
        response = HTTPResponse(
            200,
            body=request.headers["User-Agent"].encode("utf-8"),
            headers={"Content-Type": "text/plain"},
        )
        conn.sendall(bytes(response))
    elif request.path.startswith("/files"):
        if request.method == "GET":
            filename = request.path.split("/files/")[1]
            file_path = os.path.join(data_directory, filename)

            if os.path.isfile(file_path):
                response = HTTPResponse(
                    200,
                    body=open(file_path, "rb").read(),
                    headers={"Content-Type": "application/octet-stream"},
                )
                conn.sendall(bytes(response))
            else:
                conn.sendall(bytes(HTTPResponse(404)))
        elif request.method == "POST":
            filename = request.path.split("/files/")[1]
            file_path = os.path.join(data_directory, filename)

            with open(file_path, "wb") as f:
                f.write(request.body)

            conn.sendall(bytes(HTTPResponse(201)))
        else:
            conn.sendall(bytes(HTTPResponse(404)))
    else:
        conn.sendall(bytes(HTTPResponse(404)))

    conn.close()


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--directory", default=os.getcwd())
    arg_parser.add_argument("--host", default=HOST)
    arg_parser.add_argument("--port", default=PORT)

    args = arg_parser.parse_args()

    data_directory = args.directory

    server_socket = socket.create_server((args.host, int(args.port)), reuse_port=True)

    while True:
        conn, addr = server_socket.accept()
        print("Connected by", addr)
        thread = threading.Thread(target=handle_connection, args=(conn, data_directory))
        thread.start()


if __name__ == "__main__":
    main()

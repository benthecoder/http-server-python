import pytest
import threading
import socket
from http_server.http_server import main

HOST = "127.0.0.1"
PORT = 4221


@pytest.fixture(scope="module", autouse=True)
def start_server():
    server_thread = threading.Thread(target=main)
    server_thread.daemon = True
    server_thread.start()


@pytest.mark.parametrize(
    "method, path, body, expected_status_code, expected_body",
    [
        ("GET", "/", "", 200, ""),
        ("GET", "/echo/test", "", 200, "test"),
        ("GET", "/user-agent", "", 200, "test-agent"),
        ("GET", "/files/data/sample.txt", "", 200, "test"),
        ("GET", "/files/nonexistent.txt", "", 404, ""),
        ("POST", "/files/data/test.txt", "new-content", 201, ""),
    ],
)
def test_integration(method, path, body, expected_status_code, expected_body):
    headers = ["User-Agent: test-agent"]
    if body:
        headers.append(f"Content-Length: {len(body)}")

    raw_request = (
        f"{method} {path} HTTP/1.1\r\n" + "\r\n".join(headers) + "\r\n\r\n" + body
    )
    if body is not None:
        raw_request += body

    with socket.create_connection((HOST, PORT)) as sock:
        sock.sendall(raw_request.encode())
        response = sock.recv(1024).decode()

    status_code, body = parse_response(response)
    assert status_code == expected_status_code
    assert body == expected_body


def parse_response(response):
    """
    example response: 'HTTP/1.1 201\r\nContent-Length: 0\r\n\r\n'
    """
    response = response.split("\r\n\r\n")
    parts = response[0]
    body = response[1]

    parts = parts.split("\r\n")
    status_line = parts[0]
    _, status_code, *_ = status_line.split(" ")
    headers = parts[1:]
    return int(status_code), body

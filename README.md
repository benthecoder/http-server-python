# A simple HTTP server in Python

From the ["Build Your Own HTTP server" Challenge](https://app.codecrafters.io/courses/http-server/overview)

This is a simple HTTP server written in Python.

It runs on your machine's localhost and listens on port 4221. Any HTTP client like a browser, curl or a network library such as Python's `requests` can interact with this server.

This HTTP Server allows multiple client connections and handles different types of HTTP requests and responses. The server is built with the simplicity and ease in handling http request-response cycle.

## Interacting with the server

You have the option to run the server from a chosen directory or from the current working directory. You can also specify the host and the port number which you want this server to listen on.

To run the server, use the following command:

```bash
python http_server/http_server.py
```

Or using make command:

```bash
make start_server
```

To specify both a directory, host, and port, use the following command:

```bash
python http_server/http_server.py \
  --directory your/directory/path \
  --host your_host \
  --port your_port_number
```

The default host is `127.0.0.1 (localhost)` and the default port is `4221`.

### Request:

You can send the HTTP request to the server with a method, path, headers, and body.

The path can be one of the following:

- `/` - It returns a 200 status response
- `/echo/something` - It returns an HTTP response with a body of 'something'
- `/user-agent` - It will return the user agent that is sent in headers of the request
- `/files/filename`
  - If the method is `GET`, returns the content of the specified file. If the file does not exist, it will return a 404 not found error.
  - If the method is `POST`, creates a file with your body content, if file is already exists, it overwrites the file content. Otherwise, the server will return a 404 not found error.

### Response:

The server will return a response with status code, headers, and body (if any).

#### Example of response:

```text
  HTTP/1.1 200 OK
  Content-Length: 9
  Content-Type: text/plain

  something
```

This response indicates a 200 status code with a body of 'something'.

## Running Tests

```bash
pytest
```

This will run the tests to ensure the http server is working correctly.

## Resources

- [Pytest vs Unittest (Honest Review Of The 2 Most Popular Python Testing Frameworks) | Pytest With Eric](https://pytest-with-eric.com/comparisons/pytest-vs-unittest/#Recommendation-Unittest-vs-Pytest)

- [HTTP Made Really Easy](https://www.jmarshall.com/easy/http/#whatis)

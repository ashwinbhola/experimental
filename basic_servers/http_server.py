import json
import socket
from concurrent.futures import ThreadPoolExecutor

HOST = "127.0.0.1"  # localhost
PORT = 8080
# carriage return line feed delimiter for terminating lines in http request
CRLF_DELIMITER = "\r\n"


def get_root_handler():
    return {"message": "Hello, client!"}


def post_search_handler():
    return {"message": "Howdie, client!"}


API_REQUEST_HANDLERS = {
    "GET": {"/": get_root_handler},
    "POST": {"/search": post_search_handler},
}


def form_response(status, response_data, headers):
    response_body = json.dumps(response_data)
    response = (
        f"HTTP/1.1 {status}{CRLF_DELIMITER}"
        f"{headers}{CRLF_DELIMITER}"
        f"Content-Length: {len(response_body)}{CRLF_DELIMITER}{CRLF_DELIMITER}"
        f"{response_body}{CRLF_DELIMITER}"
    )

    return response


def handle_request(method, path, request_body):
    """Request handler."""
    headers = "Content-Type: application/json"
    method_request_handler = API_REQUEST_HANDLERS.get(method)
    if method_request_handler is None:
        status = "405 Method Not Allowed"
        response_data = {"message": f"{method} not recognized by the server"}
        return form_response(status, response_data, headers)

    method_path_request_handler = method_request_handler.get(path)
    if method_path_request_handler is None:
        status = "404 Not Found"
        response_data = {"message": f"{path} not recognized by the server for {method}"}
        return form_response(status, response_data, headers)

    try:
        status = "200 OK"
        response_data = method_path_request_handler()
    except:
        status = "500 Internal Server Error"
        response_data = {"message": "Error when processing th request."}

    return form_response(status, response_data, headers)


def parse_header(header_lines):
    """Prases the header string into a dictionary."""
    headers = {}
    for header_line in header_lines:
        if header_line == "":
            break
        if ":" not in header_line:
            continue
        
        header_key, header_val = header_line.split(": ", 1)
        headers[header_key.lower()] = header_val.strip()

    return headers


def recv_client_request(client_conn):
    """Recieve client request in full."""
    full_message = b""
    blank_line_delim = f"{CRLF_DELIMITER}{CRLF_DELIMITER}".encode("utf-8")

    while blank_line_delim not in full_message:
        message = client_conn.recv(10)
        if not message:
            return None  # None here would make the server terminate the connection
        full_message += message

    header_data, _, request_body = full_message.partition(blank_line_delim)

    request_lines = header_data.decode("utf-8").split(CRLF_DELIMITER)
    # the first line of a request is of the format "<http_method> <request_target> <http_version>"
    request_line = request_lines[0]
    method, path, _ = request_line.split()

    # In standard HTTP/1.1 GET requests, everything after 
    # the first line and before blank line is part of the headers
    headers = parse_header(request_lines[1:])

    if "content-length" not in headers:
        return (method, path, headers, None)
    
    # keep recieiving the remaining bytes of request body
    # until we have covered content_length bytes
    content_length = int(headers["content-length"])
    while len(request_body) < content_length:
        message = client_conn.recv(10)
        if not message:
            return None  # None here would make the server terminate the connection
        request_body += message
    
    return (method, path, headers, request_body.decode("utf-8"))

    

def handle_client(client_conn, client_address):
    """Client handler."""
    while True:
        try:
            client_request = recv_client_request(client_conn)

            if client_request is None:
                # Exit the infinite while loop if the client has terminated the connection
                print(f"Client {client_address} has terminated the connection")
                break
            
            method, path, headers, request_body = client_request
            print(f"[{client_address}] -> {client_request}")

        except Exception as exc:
            print(f"Exception: {exc}")

            error_response_data = {"message":  "Illformed request"}
            error_response_status = "400 Bad Request"
            error_response = form_response(
                error_response_status, error_response_data, "Content-Type: application/json"
            )

            # send the 400 error response to the client
            client_conn.sendall(error_response.encode("utf-8"))

            # close the connection on recieving an illformed request
            client_conn.close()
            print(f"Terminated the connection with client {client_address}")
            break
        
        response = handle_request(method, path, request_body)
        
        # Unlike send(), this method continues to send data 
        # from bytes until either all data has been sent or an error occurs
        client_conn.sendall(response.encode("utf-8"))

        client_conn_pref = headers.get("connection", "").lower()
        if client_conn_pref != "keep-alive":
        # Terminate the connection with client after sending the response
            client_conn.close()
            print(f"Terminated the connection with client {client_address}")
            break


def start_server():
    # create a TCP socket instance using a context handler to allow
    # cleaner shutdown of sockets on exception
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        # bind the tcp socket to localhost IPv4 and a port
        tcp_socket.bind((HOST, PORT))
        print(f"Server is running at http://{HOST}:{PORT}")

        # listen for connections from clients
        tcp_socket.listen()

        # create a thread pool to handle concurrent clients
        with ThreadPoolExecutor(max_workers=5) as executor:
            try:
                while True:
                    # wait for an incoming connection
                    conn, client_address = tcp_socket.accept()
                    # conn is the client socket object we'll use from
                    # now to communicate with the client
                    executor.submit(handle_client, conn, client_address)
            except KeyboardInterrupt:
                print("Shutting down.")
            except Exception as exc:
                print(exc)


if __name__ == "__main__":
    start_server()
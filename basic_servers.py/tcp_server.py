import socket
from concurrent.futures import ThreadPoolExecutor

HOST = "127.0.0.1"  # localhost
PORT = 8080


def handle_request(request_msg):
    """Request handler."""
    return f"Processed: {request_msg}"


def handle_client(client_conn, client_address):
    """Client handler."""
    with client_conn:
        while True:
            message = client_conn.recv(1024).decode("utf-8")
            print(f"[{client_address}] -> {message}")
            if not message:
                # Exit the infinite while loop if the client has terminated the connection
                print(f"Terminated the connection with client: {client_address}")
                break
            
            response = handle_request(message)
            
            # Unlike send(), this method continues to send data 
            # from bytes until either all data has been sent or an error occurs
            client_conn.sendall(response.encode("utf-8"))


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
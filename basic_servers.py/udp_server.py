import socket
from concurrent.futures import ThreadPoolExecutor

HOST = "127.0.0.1"  # localhost
PORT = 8080


def handle_request(data, client_address, udp_socket):
    """Function to handle a single request"""
    message = data.decode("utf-8")
    print(f"[{client_address}] -> {message}")

    # Simulate processing (can be extended)
    response = f"Processed: {message}"
    udp_socket.sendto(response.encode("utf-8"), client_address)


def start_server():
    # create a UDP socket instance using a context handler to allow
    # cleaner shutdown of sockets on exception
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        # bind the udp socket to localhost IPv4 and a port
        udp_socket.bind((HOST, PORT))
        print(f"Server is running at http://{HOST}:{PORT}")

        # create a thread pool to handle concurrent clients
        with ThreadPoolExecutor(max_workers=10) as executor:
            try:
                while True:
                    received_bytes, client_address = udp_socket.recvfrom(1024)
                    print(f"Client Address: {client_address}")
                    # Submit each request to `handle_request`
                    executor.submit(
                        handle_request, received_bytes, client_address, udp_socket
                    )
                    
            except KeyboardInterrupt:
                print("Shutting down.")
            except Exception as exc:
                print(exc)


if __name__ == "__main__":
    start_server()
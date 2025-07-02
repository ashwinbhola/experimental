import socket
import threading

LB_HOST = "127.0.0.1"  # localhost
LB_PORT = 8080

class LoadBalancer:
    def __init__(self, backends):
        self.backends = backends
        self.to_choose = 0
        self.lock = threading.Lock()
    
    def get_next_backend(self):
        with self.lock:
            backend = self.backends[self.to_choose]
             # Move to next backend, wrap around
            self.to_choose = (self.to_choose + 1) % len(self.backends)
            return backend

    
    def handle_client(self, client_socket):
        backend = self.get_next_backend()
        print(f"Forwarding client to backend {backend}")

        try:
            # open a socket that is connected to backend
            # so we can send tcp segments from client
            # to backend
            backend_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM
            )
            backend_socket.connect(backend)

            # Start 2 threads so data can be concurrently transferred
            # between the client and the backend

            threading.Thread(
                target=self.forward_segments,
                args=(client_socket, backend_socket),
            ).start()

            threading.Thread(
                target=self.forward_segments,
                args=(backend_socket, client_socket),
            ).start()
        
        except Exception as exc:
             # If backend connection fails, close client connection and print error
            print(f"Error connecting to backend: {exc}")
            client_socket.close()
        
    def forward_segments(self, from_socket, to_socket):
        try:
            while True:
                # Receive up to 4096 bytes
                data = from_socket.recv(4096)

                if not data:
                    # Exit the infinite while loop if the client has terminated the connection
                    print(f"Client has terminated the connection")
                    break

                to_socket.sendall(data)
        except:
            pass
        finally:
            # Close both sockets when done forwarding
            from_socket.close()
            to_socket.close()
    
    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((LB_HOST, LB_PORT))

        # allow up to 100 queued connections
        server.listen(100)

        print(f"Load balancer listening on {LB_HOST}:{LB_PORT}")

        while True:
            # # wait for an incoming connection
            client_socket, addr = server.accept()
            print(f"Received connection from {addr}")

            # client_socket is the socket object we'll use from
            # now to communicate with the client
            # # Handle the client connection in a new thread to 
            # allow multiple clients concurrently
            threading.Thread(
                target=self.handle_client,
                args=(client_socket, ),
            ).start()


if __name__ == "__main__":
    backends = [
        ('127.0.0.1', 9001),
        ('127.0.0.1', 9002),
        # Add more backends if needed
    ]
    lb = LoadBalancer(backends)
    lb.run()
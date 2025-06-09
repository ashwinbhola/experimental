import socket
import time
from multiprocessing import Process

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 8080  # The port used by the server
NUM_CLIENTS = 8
NUM_REQUESTS_PER_CLIENT = 3

def client_task(client_id):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        for req_idx in range(NUM_REQUESTS_PER_CLIENT):
            request = f"Hello, server. This is request {req_idx} from client {client_id}"
            s.sendall(request.encode("utf-8"))

            response = s.recv(1024)

            print(f"Client {client_id} received {response.decode('utf-8')} for {req_idx=}")
        
        # time.sleep(20)

def run_clients():
    processes = []
    for i in range(NUM_CLIENTS):
        p = Process(target=client_task, args=(i,))
        p.start()
        processes.append(p)

    # Wait for all processes to complete
    for p in processes:
        p.join()

if __name__ == "__main__":
    run_clients()
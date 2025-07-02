import socket
import threading

def handle_client(client_socket):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            
            # Send the received data back to the client
            client_socket.sendall(data)
    except:
        pass
    finally:
        client_socket.close()
        print(f"Connection closed")

def run_echo_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Echo server running on {host}:{port}")

    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr}")

        threading.Thread(
            target=handle_client, args=(client_socket, )
        ).start()
        

if __name__ == "__main__":
    # Change these as needed
    HOST = '127.0.0.1'

    # Run two echo servers sequentially in different terminals or different scripts:
    # 1st server on port 9001
    run_echo_server(HOST, 9001)

    # 2nd server on port 9002
    # run_echo_server(HOST, 9002)
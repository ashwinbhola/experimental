import asyncio
import websockets

SERVER_ADDRESS = "127.0.0.1"
SERVER_PORT = 8080

connected_clients = set()


async def echo(websocket):
    """
    Every time a new user joins, this function runs for that client.
    Logic for receiving messages from clients and 
    sending messages to other connected clients.
    """
    # add the client connection to connected clients set
    # to keep track of which clients are online right now
    connected_clients.add(websocket)
    print(f"Client connected, {len(connected_clients)=}")
    
    try:
        # Wait for messages from the client in a non-blocking way.
        # Every time the client sends a message,
        # we loops and handle it
        async for msg in websocket:
            print(f"Received: {msg}")

            # Send the message to everyone except the sender
            for client in connected_clients:
                if client != websocket:
                    await client.send(msg)

    except websockets.exceptions.ConnectionClosed:
        print("=== Abnormal connection closure ===")
    finally:
        connected_clients.remove(websocket)
        print(f"Close code: {websocket.close_code}")
        print(f"Reason: {websocket.close_reason}")
        print("======")


async def process_request(path, request):
    """Print the websocket http handshake request headers and path."""
    print("=== Handshake Request ===")
    print(f"Request path: {request.path}")
    for header, value in request.headers.raw_items():
        print(f"{header}: {value}")
    print("=================================")
    return None  # Accept the connection


async def main():
    # Start a WebSocket server in a non-blocking way.
    # process_request is an optional function to handle HTTP handshake logic,
    # such as authentication or custom headers
    server = await websockets.serve(
        echo, SERVER_ADDRESS, SERVER_PORT, process_request=process_request
    )
    print(f"Server started at ws://{SERVER_ADDRESS}:{SERVER_PORT}")
    await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
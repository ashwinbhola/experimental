import asyncio
import websockets

SERVER_ADDRESS = "127.0.0.1"
SERVER_PORT = 8080

connected_clients = set()

async def echo(websocket):
    connected_clients.add(websocket)
    print(f"Client connected, {len(connected_clients)=}")
    
    try:
        async for msg in websocket:
            print(f"Received: {msg}")
            for client in connected_clients:
                if client != websocket:
                    await client.send(msg)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected.")
    finally:
        connected_clients.remove(websocket)


async def main():
    server = await websockets.serve(echo, SERVER_ADDRESS, SERVER_PORT)
    print(f"Server started at ws://{SERVER_ADDRESS}:{SERVER_PORT}")
    await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
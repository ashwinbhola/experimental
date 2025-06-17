import asyncio
import websockets
import sys


async def send_messages(server):
    """Send messages typed by the user to the server."""
    # Get the current running event loop
    loop = asyncio.get_event_loop()

    while True:        
        # input is blocking and its neither a coroutine function nor has an
        # __await__ method implemented. The way to run such functions
        # in an async non blocking way is to run them in a separate thread
        # which run_in_executor helps us accomplish
        message = await loop.run_in_executor(None, input, "You: ")
        message = message.strip()

        if message.lower() == "quit":
            await server.close(code=1000, reason="Client says bye")
            break

        await server.send(message)


async def receive_messages(server):
    """An async coroutine that continuously receives messages from a server."""
    try:
        while True:
            # Wait asynchronously to receive message from the websocket server
            message = await server.recv()
            # flush=True makes sure the prompt shows immediately
            print(f"\nReceived: {message}\nYou: ", end="", flush=True)
    except websockets.exceptions.ConnectionClosed:
        # This exception is raised when the websocket connection 
        # is closed (by the server or the client)
        print("=== Client closed ===")
        print(f"Close code: {server.close_code}")
        print(f"Reason: {server.close_reason}")
        print("======")     


async def main():
    server_address = "ws://127.0.0.1:8080"
    server = await websockets.connect(server_address)

    # print the websocket http handshake response body and headers
    print("=== Handshake Response ===")
    print(f"Response body: {server.response.body.decode('utf-8')}")
    print(f"Response reason: {server.response.reason_phrase}")
    for header, value in server.response.headers.raw_items():
        print(f"{header}: {value}")
    print("==================================")

    # A client should be able to send and receive messages simulataneously.
    # Pause the current coroutine until both tasks passes
    # to gather are complete. Both tasks, of sending and receiving messages
    # are started simultaneously and run concurrently without blocking
    # each other
    await asyncio.gather(
        send_messages(server),
        receive_messages(server)
    )


if __name__ == "__main__":
    asyncio.run(main())
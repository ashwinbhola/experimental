import asyncio
import websockets
import sys

async def send_messages(server):
    loop = asyncio.get_event_loop()
    while True:
        print("You: ", end="", flush=True)
        message = await loop.run_in_executor(None, sys.stdin.readline)
        message = message.strip()
        if message.lower() == "quit":
            await server.close()
            break
        await server.send(message)


async def receive_messages(server):
    try:
        while True:
            message = await server.recv()
            print(f"\nReceived: {message}\nYou: ", end="", flush=True)
    except websockets.exceptions.ConnectionClosed:
        print("\nDisconnected from server.")


async def main():
    server_address = "ws://127.0.0.1:8080"
    server = await websockets.connect(server_address)

    await asyncio.gather(
        send_messages(server),
        receive_messages(server)
    )

    # # Run send and receive tasks concurrently
    # send_task = asyncio.create_task(send_messages(server))
    # receive_task = asyncio.create_task(receive_messages(server))

    # # Wait until either send or receive finishes (e.g. user quits or connection closes)
    # done, pending = await asyncio.wait(
    #     [send_task, receive_task],
    #     return_when=asyncio.FIRST_COMPLETED,
    # )

    # # Cancel the other task
    # for task in pending:
    #     task.cancel()



if __name__ == "__main__":
    asyncio.run(main())
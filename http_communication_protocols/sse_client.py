import requests
import sseclient
from multiprocessing import Process
import time

def sender_task():
    # sender sends a message to the server every 5 seconds
    for msg_idx in range(5):
        time.sleep(5)
        # sends a message
        res = requests.post(
            "http://localhost:8080/send",
            json={"message": f"msg_{msg_idx}"}
        )
        msg_idx += 1

def subscriber_task():
    """Listens for incoming events from the server."""
    
    sub_url = "http://localhost:8080/subscribe"

    # stream=True opens a long-lived HTTP connection that 
    # doesn't close after one response and reads new data as 
    # server sends it -- the read the response in chunks
    # i.e.the entire response is not downloaded into memory at once
    with requests.get(sub_url, stream=True) as response:
        # Turns streaming HTTP response chunks into a stream of parsed SSE events
        client = sseclient.SSEClient(response)

        # client.events() is an iterator that
        # gives you one event at a time from the SSE 
        # stream (which is a never ending connection)
        # and waits if no message is there yet
        for event in client.events():
            print(f"Received: {event.data}")


def run_clients():
    """Run sender and subscriber as separate processes."""
    processes = []
    sender_process = Process(target=sender_task)
    subscriber_process = Process(target=subscriber_task)
    subscriber_process.start()
    sender_process.start()

    # Wait for all processes to complete
    sender_process.join()
    subscriber_process.join()

if __name__ == "__main__":
    run_clients()

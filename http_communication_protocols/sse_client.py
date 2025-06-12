import requests
import sseclient
from multiprocessing import Process
import time

def sender_task():
    for msg_idx in range(5):
        time.sleep(5)
        # sends a message
        res = requests.post(
            "http://localhost:8080/send",
            json={"message": f"msg_{msg_idx}"}
        )
        msg_idx += 1

def subscriber_task():
    sub_url = "http://localhost:8080/subscribe"
    with requests.get(sub_url, stream=True) as response:
        client = sseclient.SSEClient(response)

        for event in client.events():
            print(f"Received: {event.data}")


def run_clients():
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

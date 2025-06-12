import requests
from multiprocessing import Process
import time

def sender_task():
    for msg_idx in range(5):
    # sends a message
        res = requests.post(
            "http://localhost:8080/send",
            json={"message": f"msg_{msg_idx}"}
        )
        # print("Sender Response: ", res.text)
        msg_idx += 1
        time.sleep(5)

def poller_task():
    # poll the message
    msg_id = None
    polling_url = "http://localhost:8080/poll"
    for _ in range(15):
        if msg_id is not None:
            polling_url = f"http://localhost:8080/poll?last_id={msg_id}"
        res = requests.get(
            polling_url,
        )
        new_msgs = res.json()
        print("Poller Response: ", new_msgs)
        if new_msgs:
            msg_id = new_msgs[-1]["id"]
        time.sleep(2)

def long_poller_task():
    # poll the message
    msg_id = None
    polling_url = "http://localhost:8080/long_poll"
    for _ in range(5):
        if msg_id is not None:
            polling_url = f"http://localhost:8080/long_poll?last_id={msg_id}"
        res = requests.get(
            polling_url,
        )
        new_msgs = res.json()
        print("Long Poller Response: ", new_msgs)
        if new_msgs:
            msg_id = new_msgs[-1]["id"]
        time.sleep(2)

def run_clients():
    processes = []
    sender_process = Process(target=sender_task)
    poller_process = Process(target=long_poller_task)
    sender_process.start()
    poller_process.start()

    # Wait for all processes to complete
    sender_process.join()
    poller_process.join()

if __name__ == "__main__":
    res = requests.get(
        "http://localhost:8080/clear",
    )
    run_clients()

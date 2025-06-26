import redis

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
CHANNEL = "TEST"


def start_publisher():
    publisher = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

    while True:
        message = input("Msg: ")

        if message == "quit":
            break

        num_subscribers_delivered = publisher.publish(CHANNEL, message)
        print(f"Message {message} delivered to {num_subscribers_delivered} subscribers")


if __name__ == "__main__":
    start_publisher()
import redis

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
CHANNEL = "TEST"


def start_consumer():
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

    # Create a PubSub object and subscribe to a channel
    # With this object, you can subscribe to channels 
    # and listen for messages that get published to them
    pubsub = redis_client.pubsub()
    pubsub.subscribe(CHANNEL)

    print(f"Subscribed to {CHANNEL} channel. Waiting for messages...")

    for msg in pubsub.listen():
        if msg['type'] in ('message', 'pmessage'):
            print(f"Got: {msg['data'].decode()}")


if __name__ == "__main__":
    start_consumer()
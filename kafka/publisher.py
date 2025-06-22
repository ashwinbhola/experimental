from confluent_kafka import Producer
import json
import random

# set the bootstrap server in the config
CONF = {
    "bootstrap.servers": "localhost:9092"
}
TOPIC = "test-topic"


def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(
            f"Message {msg.value()} delivered to topic: {msg.topic()} partition: [{msg.partition()}]"
        )


def main():
    producer = Producer(CONF)

    while True:
        username = input("Username: ")
        if username == "quit":
            break

        user_input = input("Publish: ")

        message = json.dumps({
            "user": username,
            "msg": user_input,
        }) 

        # Asynchronously produce a message. The delivery 
        # report callback will be triggered 
        # from the call to poll() above
        producer.produce(
            topic=TOPIC, 
            key=username,  # same key goes to the same partition
            value=message, 
            callback=delivery_report
        )

        # produce method queues the messages in the local buffer
        # and the actual delivery to kafka brokers happens aync.
        # poll(0) triggers the execution of delivery callbacks
        # for all completed message delivery events. Also, poll(0)
        # is non-blocking i.e. it just runs the callbacks for messages 
        # that have finished sending "up to that moment". Messages waiting 
        # to be sent would have their callback triggered in later poll(0) calls
        producer.poll(0)

    # Blocks until all messages sent and callbacks done
    producer.flush()


if __name__ == "__main__":
    main()

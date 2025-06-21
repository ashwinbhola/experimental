from confluent_kafka import Consumer, KafkaException

CONF = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "CONSUMER_GROUP_TEST",
    "auto.offset.reset": "earliest",
    # "debug": "cgrp,topic,fetch"
}
TOPIC = "test-topic"


def on_assign(consumer, partitions):
    # Inspect the assigned partitions
    print("Assigned partitions:")
    for partition in partitions:
        print(f"    Topic: {partition.topic}, Partition: {partition.partition}")
    
    # Accept the assignment by calling consumer.assign(partitions)
    consumer.assign(partitions)  # IMPORTANT: this tells Kafka you're ready to consume


def main():
    consumer = Consumer(CONF)

    # on_assign is called:
    # 1. When the consumer first connects and gets assigned partitions
    # 2. When there’s a rebalance (e.g., a consumer joins or leaves the group)
    consumer.subscribe([TOPIC], on_assign=on_assign)

    print("Waiting for messages")

    try:
        while True:
            msg = consumer.poll(1.0)  # timeout in seconds
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                print(f"Received message: {msg.value()} (key={msg.key()})")
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
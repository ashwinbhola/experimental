import pika
import time

BROKER_HOST = "127.0.0.1"
BROKER_PORT = 5672

credentials = pika.PlainCredentials('guest', 'guest')

def message_callback(ch, method, properties, body):
    print(f"[X] Received {body.decode()}")
    # to check the delay in getting messages if the consumer is busy 
    time.sleep(5)

# Blocking connection ensures that all operations 
# (e.g. declare queue, publish, consume) are blocking
# i.e. your program stops and waits for the broker to respond 
# before continuing
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        BROKER_HOST, BROKER_PORT, credentials=credentials
    ),
)

# Once the TCP connection is established, we open
# a channel (the primary communication unit in RabbitMQ) 
# within that connection and all operations (declaring queues, 
# publish, consume) happen on the channel. A connection can have 
# many such channels
channel = connection.channel()


channel.basic_consume(queue="proto_queue",
                      on_message_callback=message_callback,
                      auto_ack=True)

try:
    print("[*] Waiting for messages.")
    channel.start_consuming()
except KeyboardInterrupt:
    print("Shutting down...")
    channel.stop_consuming()
    connection.close()
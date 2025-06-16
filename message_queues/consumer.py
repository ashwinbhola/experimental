import pika

BROKER_HOST = "127.0.0.1"
BROKER_PORT = 8080

def message_callback(ch, method, properties, body):
    print(f" [X] Received {body.decode()}")

# Blocking connection ensures that all operations 
# (e.g. declare queue, publish, consume) are blocking
# i.e. your program stops and waits for the broker to respond 
# before continuing
connection = pika.BlockingConnection(
    pika.ConnectionParameters(BROKER_HOST, BROKER_PORT)
)

# Once the TCP connection is established, we open
# a channel (the primary communication unit in RabbitMQ) 
# within that connection and all operations (declaring queues, 
# publish, consume) happen on the channel. A connection can have 
# many such channels
channel = connection.channel()

# Declare exchange of type "direct". A direct exchange delivers a 
# message to its bound queues with a matching routing key
# channel.exchange_declare(exchange="proto_exch", exchange_type="direct")

channel.basic_consume(queue="proto_queue",
                      on_message_callback=message_callback,
                      auto_ack=True)

print(" [*] Waiting for messages.")
channel.start_consuming()
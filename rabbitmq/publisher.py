import pika

BROKER_HOST = "127.0.0.1"
BROKER_PORT = 5672

credentials = pika.PlainCredentials('guest', 'guest')

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

# Declare exchange of type "direct". A direct exchange delivers a 
# message to its bound queues with a matching routing key
# channel.exchange_declare(exchange="proto_exch", exchange_type="direct")

while True:
    message = input("You: ")
    if message == "quit":
        break
    
    # Publish message to the exchange with routing key 'info'
    channel.basic_publish(
        exchange="proto_exch",
        routing_key="info",
        body=message
    )
    print(" [X] Sent message")

connection.close()
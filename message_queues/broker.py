import pika

BROKER_HOST = "127.0.0.1"
BROKER_PORT = 5672

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
channel.exchange_declare(exchange="proto_exch", exchange_type="direct")

# Declare a queue; durability ensures queue persistance i.e.
# queue comes back up after a RabbitMQ server restart (not to
# be confused with message persistence)
result = channel.queue_declare(queue="proto_queue", durable=True)

# Bind the queue to the exchange with a routing key
channel.queue_bind(exchange="proto_exch", queue="proto_queue", routing_key="info")

connection.close()

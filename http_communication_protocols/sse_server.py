from flask import Flask, Response, request
import queue
import json

subscribers = []

app = Flask(__name__)


def event_stream(subscriber_queue):
    """
    Generator that keeps yielding messages from the subscribers' queue to the client.
    """

    # Runs forever, streaming data as long as the connection is alive
    while True:
        try:
            # Waits up to 30 seconds for a new message from the queue
            # If no message arrives in 30 seconds, it raises queue.Empty
            msg = subscriber_queue.get(timeout=30)

            # Format the `msg` as an SSE message and
            # send this chunk back to the HTTP response stream
            yield f"data: {json.dumps(msg)}\n\n"
        except queue.Empty:
            # Keep the connection alive
            # This is a heartbeat or keep-alive ping to prevent 
            # timeouts or connection drops. 
            # `:` starts a comment in SSE -- The client ignores comment 
            # lines but sees the connection is still alive
            yield ": keep-alive\n\n"

@app.route("/subscribe")
def subscribe():
    """
    Adds a queue for the subscriber in the `subscribers` list.
    Returns a streaming response using event_stream(...) generator
    to send data over time.
    """
    subscriber_queue = queue.Queue()
    subscribers.append(subscriber_queue)

    # The special content_type text/event-stream tells the client
    # that this is a Server-Sent Events stream — keep the connection 
    # open and listen for updates
    return Response(
        event_stream(subscriber_queue),
        content_type="text/event-stream"
    )


@app.route("/send", methods=['POST'])
def send():
    """
    Adds the message received in all the queues 
    within the `subscribers` list.
    """
    msg = request.json.get("message")
    if msg:
        for sub in subscribers:
            sub.put({"message": msg})
    
    return {"status": "Message received!"}


if __name__ == '__main__':
    app.run(
        host="127.0.0.1", port=8080, debug=True, threaded=True
    )
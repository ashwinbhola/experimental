from flask import Flask, Response, request
import queue
import json

subscribers = []

app = Flask(__name__)


def event_stream(subscriber_queue):
    while True:
        try:
            msg = subscriber_queue.get(timeout=30)
            yield f"data: {json.dumps(msg)}\n\n"
        except queue.Empty:
            # Keep the connection alive
            yield ": keep-alive\n\n"

@app.route("/subscribe")
def subscribe():
    subscriber_queue = queue.Queue()
    subscribers.append(subscriber_queue)

    return Response(
        event_stream(subscriber_queue),
        content_type="text/event-stream"
    )


@app.route("/send", methods=['POST'])
def send():
    msg = request.json.get("message")
    if msg:
        for sub in subscribers:
            sub.put({"message": msg})
    
    return {"status": "Message received!"}


if __name__ == '__main__':
    app.run(
        host="127.0.0.1", port=8080, debug=True, threaded=True
    )
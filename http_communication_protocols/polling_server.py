from flask import Flask, request, jsonify
import threading
import time


app = Flask(__name__)

messages = []
message_lock = threading.Lock()

LONG_POLLING_TIMEOUT = 20

@app.route("/long_poll")
def long_poll():
    last_msg_id = request.args.get("last_id", -1)
    start_time = time.time()

    while time.time() - start_time < LONG_POLLING_TIMEOUT:
        with message_lock:
            new_msgs = [msg for msg in messages if msg["id"] > int(last_msg_id)]
            if new_msgs:
                return jsonify(new_msgs)

            time.sleep(1)
    
    return jsonify([])


@app.route("/poll")
def poll():
    last_msg_id = request.args.get("last_id", -1)

    with message_lock:
        new_msgs = [msg for msg in messages if msg["id"] > int(last_msg_id)]
        if new_msgs:
            return jsonify(new_msgs)
    
    return jsonify([])


@app.route("/send", methods=['POST'])
def new_message():
    request_data = request.json
    with message_lock:
        msg_id = 0
        if messages:
            msg_id = messages[-1]["id"] + 1
        messages.append({
            "id": msg_id, "message": request_data["message"]
        })
    
    return {"status": "Message received!"}


@app.route("/clear")
def clear_messages():
    with message_lock:
        messages = []
    return {"message": "Cleared!"}

if __name__ == '__main__':
    app.run(
        host="127.0.0.1", port=8080, debug=True, threaded=True
    )
from flask import Flask, request, Response
import message_pb2

app = Flask(__name__)


@app.route("/embed", methods=["POST"])
def embed():
    req = message_pb2.EmbedRequest()

    # ParseFromString takes a binary string (bytes)
    # and parses it back into a protobuf message object
    req.ParseFromString(request.get_data())

    if len(req.story) > 0:
        res = message_pb2.EmbedResponse(
            embeddings=[len(req.story)] * 200
        )
        status = 200
    else:
        res = message_pb2.EmbedResponse(
            error_message="No story sent"
        )
        status = 401
    
    # SerializeToString takes a protobuf message object and
    # converts it into a compact binary format 
    # (a bytes string) to send over HTTP
    return Response(
        res.SerializeToString(),
        status=status,
        content_type="application/octet-stream"
    )


@app.route("/login", methods=["POST"])
def login():
    req = message_pb2.LoginRequest()

    # ParseFromString takes a binary string (bytes)
    # and parses it back into a protobuf message object
    req.ParseFromString(request.get_data())

    if req.username == "admin" and req.password == "secret123":
        res = message_pb2.LoginResponse(
            success=True,
            token="fake_token_123"
        )
        status = 200
    else:
        res = message_pb2.LoginResponse(
            success=False,
            error_message="Invalid credentials"
        )
        status = 401
    
    # SerializeToString takes a protobuf message object and
    # converts it into a compact binary format 
    # (a bytes string) to send over HTTP
    return Response(
        res.SerializeToString(),
        status=status,
        content_type="application/octet-stream"
    )

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True)
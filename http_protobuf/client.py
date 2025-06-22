import requests
import message_pb2


def send_protobuf(endpoint, message, response_type, session):
    binary_message = message.SerializeToString()
    resp = session.post(
        f"http://localhost:8080{endpoint}",
        data=binary_message,
        headers={"Content-Type": "application/octet-stream"}
    )
    response = response_type()

    print(f"Status code: {resp.status_code}")
    response.ParseFromString(resp.content)
    return response

session = requests.Session()  # Persistent connection

# Test /login
login_req_body = message_pb2.LoginRequest(
    username="admin", password="secret123"
)
print("[/login] =>")
res = send_protobuf(
    "/login",
    login_req_body,
    message_pb2.LoginResponse,
    session
)
print(res)

# Test /login
login_req_body = message_pb2.LoginRequest(
    username="admin", password="WrongPassword"
)
print("[/login] =>")
res = send_protobuf(
    "/login",
    login_req_body,
    message_pb2.LoginResponse,
    session
)
print(res)

# Test /embed
embed_req_body = message_pb2.EmbedRequest(
    story="Hey, Server!"
)
print("[/embed] =>")
res = send_protobuf(
    "/embed",
    embed_req_body,
    message_pb2.EmbedResponse,
    session
)
print(res.embeddings)
print("\n")

embed_req_body = message_pb2.EmbedRequest(
    story=None
)
print("[/embed] =>")
res = send_protobuf(
    "/embed",
    embed_req_body,
    message_pb2.EmbedResponse,
    session
)
print(res)
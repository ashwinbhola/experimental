from flask import Flask, request

app = Flask(__name__)

@app.before_request
def log_request_info():
    server_software = request.environ.get('SERVER_SOFTWARE', 'unknown')
    print(f"WSGI server: {server_software}")
    print("--- Request ---")
    print(f"Method: {request.method}")
    print(f"Path: {request.path}")
    print(f"Headers: {request.headers}")
    print(f"Body: {request.get_data()}")
    print("---------------")


@app.after_request
def log_response_info(response):
    print("--- Response ---")
    print(f"Status: {response.status}")
    print(f"Headers: {response.headers}")
    return response


@app.route("/")
def home():
    return "<h1>Hello, This is a HTTPS server!<h1>"

if __name__ == '__main__':
    app.run(
        ssl_context=("cert.pem", "key.pem"),
        host="127.0.0.1",
        port=8080,
        debug=True,
    )

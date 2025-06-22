To generate the python types and methods from your protobuf schema:
```
protoc --python_out=. message.proto
```
This will output `message_pb2.py`

Run the server and client then using:
```
python3 server.py
python3 client.py
```
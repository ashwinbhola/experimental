To generate message (`calculator_pb2.py`) and service class (`calculator_pb2_grpc.py`) files from the proto file:
```
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. calculator.proto
```

Run the server and the client with:
```
python3 server.py
python3 client.py
```
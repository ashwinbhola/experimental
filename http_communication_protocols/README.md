To run SSE server and client:
```
python3 sse_server.py
python3 sse_client.py
```
(These should be run in separate terminals)

To run short polling server and client:
Ensure that `poller_process` is running `poller_task` and not `long_poller_task`
```
python3 polling_server.py
python3 polling_client.py
```
(These should be run in separate terminals)

To run long polling server and client:
Ensure that `poller_process` is running `long_poller_task` and not `poller_task`
```
python3 polling_server.py
python3 polling_client.py
```
(These should be run in separate terminals)
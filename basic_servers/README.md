To run the TCP server:
```
python3 tcp_server.py
```

To run the TCP server:
```
python3 udp_server.py
```

Connecting to the TCP server using netstat:
```
netcat localhost 8080 -c
```

Connecting to the UDP server using netstat:
```
netcat localhost 8080 -c -u
```

To run the HTTP server:
```
python3 http_server.py
```

The HTTP server can be tested by sending the requests in `http_client.py`
```
python3 http_client.py
```
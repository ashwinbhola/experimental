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
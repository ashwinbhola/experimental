Start the load balancer with `python3 load_balancer.py`

Run echo server twice, changing the `PORT` in the script to 9001 and 9002: `python3 echo_server.py`

You can now use `nc 127.0.0.1 8080` on separate terminal tabs (at least 3) to test the load balancer.
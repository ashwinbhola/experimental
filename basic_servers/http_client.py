import requests

session = requests.Session()  # Persistent connection

# root server get method should work here
res = session.get(
    "http://localhost:8080/",
    headers={"Connection": "keep-alive"}
)
print(res.status_code, res.text)

# this should be using the same session as above
res = session.get(
    "http://localhost:8080/",
    headers={"Connection": "close"}
)
print(res.status_code, res.text)

# Server should see this as coming from a different port
res = session.get(
    "http://localhost:8080/",
)
print(res.status_code, res.text)

# This should return 404 error
res = session.get(
    "http://localhost:8080/search",
)
print(res.status_code, res.text)

# This should return 404 error
res = session.post(
    "http://localhost:8080/",
    data={"temp_key": "temp_val"},
)
print(res.status_code, res.text)

# This should return 405 error
res = session.put(
    "http://localhost:8080/",
    data={"temp_key": "temp_val"},
)
print(res.status_code, res.text)

# This should go to the search POST method handler in the http server
res = session.post(
    "http://localhost:8080/search",
    data={"temp_key": "temp_val"},
)
print(res.status_code, res.text)

session.close()


import requests

session = requests.Session()  # Persistent connection
res = session.get(
    "http://localhost:8080/",
    headers={"Connection": "keep-alive"}
)
print(res.status_code, res.text)

res = session.get(
    "http://localhost:8080/",
    headers={"Connection": "close"}
)
print(res.status_code, res.text)

res = session.get(
    "http://localhost:8080/",
    headers={"Connection": "close"}
)
print(res.status_code, res.text)

res = session.get(
    "http://localhost:8080/search",
    headers={"Connection": "close"}
)
print(res.status_code, res.text)

res = session.post(
    "http://localhost:8080/",
    data={"temp_key": "temp_val"},
    headers={"Connection": "close"}
)
print(res.status_code, res.text)

res = session.post(
    "http://localhost:8080/search",
    data={"temp_key": "temp_val"},
    headers={"Connection": "close"}
)
print(res.status_code, res.text)


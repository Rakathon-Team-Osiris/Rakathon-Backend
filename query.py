import requests

url = "http://127.0.0.1:5001/create"
data = {
    "username": "test_user",
    "email": "test_user@example.com"
}

response = requests.post(url, json=data)
print(response.json())

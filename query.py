import requests

url = "http://127.0.0.1:5000/analyze_skin_tone"
data = {
    "username": "test_user",
    "email": "test_user@example.com"
}

response = requests.get(url)
print(response.json())

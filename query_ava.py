import requests

url = "http://127.0.0.1:8000/fashion-advisor"  # Ensure the port matches the one your Flask app is running on
data = {
    "text_query": "Which shoes will go well with this for a formal occasion?"
}

response = requests.post(url, json=data)  # Use the 'json' parameter to send JSON data
print(response.json())

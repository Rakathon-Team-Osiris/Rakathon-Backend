import requests

url = "http://127.0.0.1:5000/analyze_skin_tone"
data = {
    "username": "test_user",
    "email": "test_user@example.com"
}

response = requests.get(url)
print(response.json())


# Sample Query Output
# {'Colour Palette': "['#0C0C0C', '#FFFFFF', '#5A5A5A', '#0000FF', '#800080']", 'Explanation': 'The user has a winter skin tone, characterized by a cool undertone and high contrast between hair, eye color, and skin tone.', 'Season': 'Winter', 'Styles': 'Opt for high contrast, bold hues such as pure white, jet black, charcoal grey, navy blue, and vivid plum. Fabrics like silk, satin, and velvet will accentuate the natural brightness in your winter complexion.'}
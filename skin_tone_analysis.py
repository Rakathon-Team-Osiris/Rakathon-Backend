import base64
import requests
import json
from dotenv import load_dotenv
import os
from PIL import Image
import io

# Load environment variables from .env file
load_dotenv()

# OpenAI API Key
api_key = os.getenv("OPENAI_API_KEY")

def encode_image(image_path, max_size=(800, 800), quality=75):
    # Open the image file
    with Image.open(image_path) as image:
        # Resize the image if it is larger than max_size
        image.thumbnail(max_size)
        
        # Save the image to a BytesIO object with compression
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=quality)
        
        # Encode the image to base64
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return img_base64

def analyze_skin_tone(image_path):
    # Define the prompt for the API
    prompt = '''You are an expert Korean color analyst specializing in personal color analysis. Your task is to analyze the user's skin tone from the provided image and offer tailored advice on color palettes and clothing styles. Follow these guidelines:

    Analyze the image carefully, focusing on the user's skin undertone and overall complexion.
    Categorize the user's skin tone into one of the four Korean seasonal color types: Spring, Summer, Autumn, or Winter.
    Provide a concise explanation of why you've chosen this season for the user in a 2 liner.
    Recommend a color palette that complements their skin tone, including specific shades for clothing in HEX codes in a python list.
    Suggest clothing styles and fabrics that would enhance their natural coloring.
    Output the above mentioned in a JSON format sample as follows:
    [{
        'Season': 'Autumn',
        'Explaination': 'demo text',
        'Colour Palette': '[demo, demo, demo]',
        'Styles': 'demo text'
    }]

    Remember to be respectful and positive in your analysis, focusing on enhancing the user's natural beauty.'''

    # Get the base64 string of the image
    base64_image = encode_image(image_path)

    # Prepare the API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-turbo",
        "messages": [
            {
                "role": "user",
                "content": prompt
            },
            {
                "role": "user",
                "content": f"data:image/jpeg;base64,{base64_image}"
            }
        ],
        "max_tokens": 1000
    }

    # Send the request to the API
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        response_json = response.json()
        content = response_json['choices'][0]['message']['content']

        # Parse the content to JSON format
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            print("Failed to parse JSON from the response.")
            result = None

        return result
    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)
        return None

image_path = "pexels-kowalievska-1055691.jpg"
output = analyze_skin_tone(image_path=image_path)

# Print the final output
if output:
    print(json.dumps(output, indent=4))
else:
    print("No output received.")

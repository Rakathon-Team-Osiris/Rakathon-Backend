from flask import Flask, request, jsonify
import os
import regex as re
import json
from dotenv import load_dotenv
from pinecone import Pinecone
import cohere
from langchain_openai import ChatOpenAI
from langchain_community.tools import TavilySearchResults
import sqlite3
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain.memory import ConversationBufferMemory
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel
import time

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")
pinecone_api_key = os.getenv("pinecone_api_key")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

pc = Pinecone(api_key=pinecone_api_key)
index = pc.Index("slay-vector-db")

co = cohere.Client(api_key=COHERE_API_KEY)

model = ChatOpenAI(model="gpt-3.5-turbo")

tool = TavilySearchResults(
    max_results=1,
    search_depth="advanced",
    include_answer=True,
    include_raw_content=True,
    include_images=True,
)

prompt = '''you are a fashion designer and an advisor. while using 'get_products()' function to retrieve products and show them, make sure you provide only the output in json format as shown below:
[{'product_title': 'sample product title',
    'product images': '[https://url1.com, https://url2.com]',
    'product_brand': 'demo brand',
    'price': 123}]
'''

connection = sqlite3.connect('fashion_data.db', check_same_thread=False)
cursor = connection.cursor()

# Load CLIP model and processor
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def extract_json_from_aimessage(ai_message):
    start_index = ai_message.find('```json')
    end_index = ai_message.find('```', start_index + 7)

    if start_index != -1 and end_index != -1:
        json_str = ai_message[start_index + 7:end_index].strip()

        try:
            json_data = json.loads(json_str)
            return json_data
        except json.JSONDecodeError:
            return None
    else:
        return None

def remove_markdown(text):
    text = re.sub(r'#\s*', '', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'^\s*[-*]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n+', '\n', text).strip()
    text = re.sub(r'\d+\.\s+', '', text)
    text = re.sub(r'\n+', ' ', text).strip()
    return text

def get_trends(query):
    '''Use this function to access internet and get latest data related to fashion'''
    answer = tool.invoke({'query': query})
    return answer

def get_products(query: str):
    ''' Use this function to pull up products from the SQL database to the user. '''
    response = co.embed(
            model='embed-multilingual-v3.0',
            texts=[query],
            input_type='classification',
            embedding_types=['float']
        )

    embedding = response.embeddings.float

    result = index.query(
        vector=embedding,
        top_k=5,
        include_values=True,
        include_metadata=True
    )

    ids = []
    for i in range(len(result['matches'])):
        match = result['matches'][i]
        id = match['id']
        ids.append(id)
    
    products = []
    for id in ids:
        cursor.execute(f'SELECT product_name, image, brand, discounted_price  FROM fashion_sql WHERE uniq_id = "{id}"')
        product = cursor.fetchall()
        products.append(product)

    return products

def describe_image(image_path):
    # Open the image
    image = Image.open(image_path)
    
    # Preprocess the image
    inputs = clip_processor(images=image, return_tensors="pt")
    
    # Move inputs to the correct device
    inputs = {k: v.to("cuda" if torch.cuda.is_available() else "cpu") for k, v in inputs.items()}
    
    # Get image features
    with torch.no_grad():
        image_features = clip_model.get_image_features(**inputs)
    
    # You might want to return these features, or further process them
    return image_features

tools = [get_trends, get_products]

memory = ConversationBufferMemory(memory_key="chat_history")

graph = create_react_agent(model, tools=tools, state_modifier=prompt)

def get_answer(text_query: str, image_path=None):
    if image_path:
        image_description = describe_image(image_path)
        combined_query = f"{image_description} {text_query}"
    else:
        combined_query = text_query

    inputs = {
        "messages": [("user", combined_query)],
        "chat_history": memory.load_memory_variables({})
    }

    stream = graph.stream(inputs, stream_mode="values")

    def get_stream(stream):
        last_message = None  
        for s in stream:
            message = s["messages"][-1]
            last_message = message 
        return last_message

    ai_message = get_stream(stream).content

    if re.search(r'\bjson\b', ai_message):
        ai_message = extract_json_from_aimessage(ai_message=ai_message)
    else:
        ai_message = remove_markdown(ai_message)

    memory.save_context({"input": combined_query}, {"output": ai_message})

    return ai_message

@app.route('/fashion-advisor', methods=['POST'])
def fashion_advisor():
    data = request.json
    text_query = data.get('text_query')
    try:
        image_path = data.get('image_path')  # Assumes image is already uploaded and available at this path
    except:
        pass
    
    if not text_query:
        return jsonify({"error": "text_query is required"}), 400

    start_time = time.time()
    response = get_answer(text_query=text_query, image_path=image_path)
    end_time = time.time()

    return jsonify({
        "response": response,
        "processing_time": f"{end_time - start_time} secs"
    })

if __name__ == '__main__':
    app.run(debug=True, port=8000)

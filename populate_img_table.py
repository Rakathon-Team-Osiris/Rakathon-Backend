import sqlite3
import feature_extractor
import requests
from PIL import Image
from io import *
from tqdm import tqdm
import ast


#################
import re
import requests

# Example list of image paths (replace this with the data from your SQLite table)
url_pattern = re.compile(r'"(http[s]?://[^"]+)"')

# Function to extract the first URL and make a GET request
def fetch_first_url(image_path):
    # Find all URLs
    urls = url_pattern.findall(image_path)
    
    # Check if we have at least one URL
    if urls:
        first_url = urls[0]
        print(f"Fetching URL: {first_url}")
        return first_url
    else:
        print("No URL found.")
        return None

#################

source_conn = sqlite3.connect('fashion_data.db')
source_cursor = source_conn.cursor()

# Connect to the destination database (slay.db)
dest_conn = sqlite3.connect('slay.db')
dest_cursor = dest_conn.cursor()

# Select only the required columns from fashion_sql
source_cursor.execute("SELECT uniq_id, product_name, image, description, tertiary FROM fashion_sql")
rows = source_cursor.fetchall()

# Insert the selected data into the images table in slay.db
for row in tqdm(rows[:10], desc="Processing rows", unit="row"):
    uniq_id, product_name, image_path, description, category,  = row
    image_path = fetch_first_url(image_path)
    # Extract the color from the image
    try:
        response = requests.get(image_path)
        image = Image.open(BytesIO(response.content))
        color = feature_extractor.get_dominant_and_central_background_color(image)
    except:
        color = "None"
    # Insert the data into the destination table
    dest_cursor.execute("INSERT INTO images (item_id, item_name, item_image, item_desc, category, color) VALUES (?, ?, ?, ?, ?, ?)", 
                        (uniq_id, product_name, image_path, description, category, color))

# Commit the transaction
dest_conn.commit()

# Close the connections
source_conn.close()
dest_conn.close()

print("Data copied successfully.")
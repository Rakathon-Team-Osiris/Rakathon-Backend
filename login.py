from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import skin_tone_analysis 

app = Flask(__name__)
CORS(app)  

def insert_user(name, phone_number, email, password, image):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    skin_tone = skin_tone_analysis.analyze_skin_tone(image)['Colour Palette']
    c.execute('''
        INSERT INTO users (name, phone_number, email, password, image, skin_tone)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, phone_number, email, password, image, skin_tone))
    conn.commit()
    conn.close()
    
def check_credentials(email, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        SELECT * FROM users WHERE email = ? AND password = ?
    ''', (email, password))
    user = c.fetchone()
    conn.close()
    return user

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"message": "Healthy"}), 200

@app.route('/create', methods=['POST'])
def create_user():
    #Input login data ->name, phone number, email, password,image,skintone
    if not request.is_json:
        return jsonify({"error": "Invalid or missing JSON"}), 400

    data = request.get_json()

    # Validate input
    required_fields = ['name', 'phone_number', 'email', 'password', 'image']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    name = data['name']
    phone_number = data['phone_number']
    email = data['email']
    password = data['password']
    image = data['image']

    # Insert user data into the SQLite table
    try:
        insert_user(name, phone_number, email, password, image)
        return jsonify({"message": "User created successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"error": "Invalid or missing JSON"}), 400

    data = request.get_json()

    # Validate input
    required_fields = ['email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    email = data['email']
    password = data['password']

    # Check credentials
    user = check_credentials(email, password)
    
    if user:
        current_user=user
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

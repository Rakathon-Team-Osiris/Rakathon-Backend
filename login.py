from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"message": "Healthy"}), 200

@app.route('/create', methods=['POST'])
def create_user():
    if not request.is_json:
        return jsonify({"error": "Invalid or missing JSON"}), 400

    data = request.get_json()
    return jsonify({"message": "Create endpoint hit", "data": data}), 200

@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"error": "Invalid or missing JSON"}), 400

    data = request.get_json()
    return jsonify({"message": "Server received the data", "data": data}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

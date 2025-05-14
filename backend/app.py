import re
from flask import Flask, request, jsonify
import requests
import pyodbc
import hashlib
import json
from flask_cors import CORS
import urllib

app = Flask(__name__)
CORS(app) 

# Azure SQL database connection configuration
SERVER = 'phishingdetection.database.windows.net'
DATABASE = 'phishingdetectiondb'
USERNAME = 'phishingdetection'
PASSWORD = 'Pass@123'
DRIVER = '{ODBC Driver 17 for SQL Server}'  

connection = f'DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'

# get database connection
def get_db_connection():
    try:
        con = pyodbc.connect(connection)
        return con
    except Exception as e:
        print(f"Database connection error: {e}")
        return None



# risk calculation on the fly
def get_risk_level(probability):
    if probability > 15:
        return 'high'
    elif probability > 10:
        return 'medium'
    else:
        return 'low'

def get_risk_color(level):
    if level == 'high':
        return 'red'
    elif level == 'medium':
        return 'yellow'
    else:
        return 'green'
    
#function for password hashing 
def hash_password(password):

    return hashlib.sha256(password.encode()).hexdigest()    

@app.route ('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        con = get_db_connection()
        if not con:
            return jsonify({"message": "Database connection error"}), 500
        
        cursor = con.cursor()
        cursor.execute("SELECT user_id, password FROM Users WHERE email = ?", (email,))
        user = cursor.fetchone()
        if not user:
         con.close()
         return jsonify({"message": "Invalid credentials"}), 401

        stored_password = user.password 
        user_id = user.user_id

        #  hash for comparison
        if hash_password(password) == stored_password:
            con.close()
            return jsonify({"message": "Login successful", "user_id": user_id}), 200
        else:
            con.close()
            return jsonify({"message": "Invalid credentials"}), 401
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500
    


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        con = get_db_connection()
        if not con:
            return jsonify({"message": "Database connection error"}), 500
        
        cursor = con.cursor()
        # delete all messages associated with the user
        cursor.execute("DELETE FROM Messages WHERE user_id = ?", (user_id,))
        
        cursor.execute("DELETE FROM Users WHERE user_id = ?", (user_id,))
        
        con.commit()
        con.close()
        return jsonify({"message": "Account deleted successfully"}), 200
        
    except Exception as e:
        print(f"Delete account error: {e}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500


@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"message": "Email and password are required"}), 400

        hashed_password = hash_password(password)  

        con = get_db_connection()
        if not con:
            return jsonify({"message": "Database connection error"}), 500

        cursor = con.cursor()


        cursor.execute(
            "INSERT INTO Users (email, password) OUTPUT INSERTED.user_id VALUES (?, ?)",
            (email, hashed_password)
        )


        user_id = cursor.fetchone()[0]

        con.commit()
        con.close()

        return jsonify({"message": "User created successfully", "user_id": user_id}), 201

    except Exception as e:
        return jsonify({"message": f"Server error: {str(e)}"}), 500

    
@app.route('/api/users/<int:user_id>/messages', methods=['POST'])
def save_message(user_id):
    try:
        data = request.json
        message_text = data.get('message')
        probability = float(data.get('probability', 0))
        
        if not message_text:
            return jsonify({"message": "Message text is required"}), 400
            
        con = get_db_connection()
        if not con:
            return jsonify({"message": "Database connection error"}), 500
            
        cursor = con.cursor()
        

        cursor.execute("""
            INSERT INTO Messages (user_id, message_text, probability)
            VALUES (?, ?, ?)
        """, (user_id, message_text, probability))
        
        con.commit()
        cursor.execute("SELECT @@IDENTITY AS message_id")
        message_id = cursor.fetchone()[0]
        con.close()
      
        return jsonify({
            "message": "Message saved successfully",
            "message_id": message_id
        }), 201
        
    except Exception as e:
        print(f"Save message error: {e}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500
    
@app.route('/api/users/<int:user_id>/messages', methods=["GET"])
def get_user_messages(user_id):
    try:
        con = get_db_connection()
        if not con:
            return jsonify({"message": "Database connection error"}), 500

        cursor = con.cursor()
        cursor.execute("""
            SELECT message_id, message_text, probability 
            FROM Messages 
            WHERE user_id = ?
        """, (user_id,))
        rows = cursor.fetchall()
        con.close()

        messages = []
        for row in rows:
            message_id, text, probability = row
            risk_level = get_risk_level(probability)
            messages.append({
                "message_id": message_id, 
                "message": text,
                "probability": probability,
                "risk": {
                    "level": risk_level,
                    "color": get_risk_color(risk_level),
                }
            })

        return jsonify({"results": messages}), 200
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return jsonify({"message": "Internal server error"}), 500



# methods to translate before checking with LECTO AI API
def is_arabic(text):
    return re.search(r'[\u0600-\u06FF]', text) is not None
def translate_to_english(text):
    url = "https://api.lecto.ai/v1/translate/text"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-Key": "78JG77E-TJS4NRF-KJYAEWP-8J15GYS"  }
    payload = {
        "texts": [text],
        "to": ["en"],
        "from": "ar"}
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        translated_text = result['translations'][0]['translated'][0]
        print(f"Original Arabic: {text}")
        print(f"Translated English: {translated_text}")
        return translated_text
    except requests.RequestException as e:
        print(f"Lecto API translation error: {e}")
        return text
@app.route('/api/phishing/check', methods=['POST'])
def check_phishing():
    try:
        data = request.json
        message_list = data.get('messages', [])
        if not message_list:
            return jsonify({"message": "No message provided"}), 400
        message = message_list[0]
        if is_arabic(message):
            message = translate_to_english(message)
        # request to Azure endpoint for our ML Model 
        azure_url = 'http://8c8f7204-18ea-4817-9651-f2005618615b.eastus.azurecontainer.io/score'
        request_data = {"data": [message]}
        body = json.dumps(request_data).encode('utf-8')
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        req = urllib.request.Request(azure_url, body, headers)
        response = urllib.request.urlopen(req)
        result = response.read().decode('utf-8')
        parsed_result = json.loads(result)
        return parsed_result, 200
        
    except urllib.error.HTTPError as e:
        return jsonify({"message": f"Error from ML service: {e.reason}", "code": e.code}), e.code
    except Exception as e:
        return jsonify({"message": f"Server error: {str(e)}"}), 500
    


@app.route('/api/users/<int:user_id>/messages/<int:message_id>', methods=['DELETE'])
def delete_user_message(user_id, message_id):
    try:
        con = get_db_connection()
        if not con:
            return jsonify({"message": "Database connection error"}), 500

        cursor = con.cursor()

        cursor.execute("""
            DELETE FROM Messages 
            WHERE message_id = ? AND user_id = ?
        """, (message_id, user_id))
        
        if cursor.rowcount == 0:
            con.close()
            return jsonify({"message": "Message not found or doesn't belong to user"}), 404

        con.commit()
        con.close()
        return jsonify({"message": "Message deleted successfully"}), 200

    except Exception as e:
        print(f"Delete message error: {e}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route('/api/users/<int:user_id>/messages', methods=['DELETE'])
def delete_all_messages(user_id):
    try:
        con = get_db_connection()
        if not con:
            return jsonify({"message": "Database connection error"}), 500

        cursor = con.cursor()
        cursor.execute("DELETE FROM Messages WHERE user_id = ?", (user_id,))
        con.commit()
        con.close()
        return jsonify({"message": "All messages deleted successfully"}), 200

    except Exception as e:
        print(f"Delete all messages error: {e}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


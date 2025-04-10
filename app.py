from flask import Flask, request, jsonify
import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Connect to MySQL Database
def get_db_connection():
    db = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    return db

@app.route('/')
def home():
    return 'Welcome to the Flask app!'

@app.route('/register', methods=['POST'])
def register_number():
    data = request.get_json()

    # Extract organization and number
    org = data.get('organization')
    number = data.get('number')

    if not org or not number:
        return jsonify({"error": "Missing organization or number"}), 400

    # Connect to MySQL
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO official_numbers (organization_name, phone_number) VALUES (%s, %s)",
            (org, number)
        )
        db.commit()
        cursor.close()
        db.close()
        return jsonify({"message": "Number registered successfully!"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500

@app.route('/lookup', methods=['GET'])
def lookup_number():
    phone_number = request.args.get('number')
    
    if not phone_number:
        return jsonify({"error": "Missing 'number' parameter"}), 400

    # Connect to MySQL
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT organization_name FROM official_numbers WHERE phone_number = %s", (phone_number,))
        result = cursor.fetchone()
        cursor.close()
        db.close()

        if result:
            return jsonify({"organization": result[0]})
        else:
            return jsonify({"message": "Number not found"}), 404
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)
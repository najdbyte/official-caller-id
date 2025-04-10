from flask import Flask, request, jsonify
from urllib.parse import urlparse
import mysql.connector
import os
from dotenv import load_dotenv
import logging
from telecom_api import simulate_telecom_api_request  # Assuming telecom_api.py exists for telecom simulation

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Parse the MYSQL_URL from environment variables
mysql_url = os.getenv('MYSQL_URL')

# Parse the MySQL connection URL
parsed_url = urlparse(mysql_url)

# Establish a database connection
def get_db_connection():
    db = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'shortline.proxy.rlwy.net'),  # Correct host
        user=os.getenv('MYSQL_USER', 'root'),  # Correct user
        password=os.getenv('MYSQL_ROOT_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE')
    )
    return db


@app.route('/')
def home():
    return "Flask app is up and running!"

# This route should be POST, not GET
@app.route('/register', methods=['POST'])
def register_number():
    data = request.get_json()

    org = data.get('organization')
    number = data.get('number')

    if not org or not number:
        return jsonify({"error": "Missing organization or number"}), 400

    # Simulate telecom API request
    telecom_response = simulate_telecom_api_request(number)

    if telecom_response['status'] == 'error':
        return jsonify(telecom_response), 400

    # Insert into MySQL
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


# This route should be GET, not POST
@app.route('/lookup', methods=['GET'])
def lookup_number():
    phone_number = request.args.get('number')
    
    if not phone_number:
        return jsonify({"error": "Missing 'number' parameter"}), 400

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


# Admin dashboard route (should be GET)
@app.route('/admin')
def admin_dashboard():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM official_numbers WHERE approved = 0")
    registrations = cursor.fetchall()
    cursor.close()
    db.close()

    return jsonify({"registrations": registrations})


# Admin approval route (should be POST)
@app.route('/admin/approve', methods=['POST'])
def approve_registration():
    data = request.get_json()
    registration_id = data.get('id')

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE official_numbers SET approved = 1 WHERE id = %s", (registration_id,))
    db.commit()
    cursor.close()
    db.close()

    return jsonify({"message": "Registration approved successfully!"}), 200


def simulate_telecom_api_request(phone_number):
    if len(phone_number) == 10:  # Simulate a basic length check for phone numbers
        return {"status": "success", "message": "Number is valid"}
    else:
        return {"status": "error", "message": "Invalid number"}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5005)))

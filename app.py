from flask import Flask, request, jsonify
from urllib.parse import urlparse
import mysql.connector
import os
from dotenv import load_dotenv
import logging
from telecom_api import simulate_telecom_api_request  # Assuming telecom_api.py exists for telecom simulation

# Configure logging to track errors or important events in production
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Load environment variables from .env
load_dotenv()

# Retrieve MYSQL_URL from environment variables
mysql_url = os.getenv('MYSQL_URL')

# Check if MYSQL_URL exists and is not None
if not mysql_url:
    raise ValueError("MYSQL_URL is not defined in environment variables")

# Parse the MySQL connection URL
parsed_url = urlparse(mysql_url)

# Ensure the port is set (if missing, set default port)
if parsed_url.port is None:
    parsed_url = parsed_url._replace(port=49052)  # Set default port (49052)

# Establish a database connection
def get_db_connection():
    db = mysql.connector.connect(
        host=parsed_url.hostname,
        user=parsed_url.username,
        password=parsed_url.password,
        database=parsed_url.path[1:],  # Remove leading '/'
        port=parsed_url.port
    )
    return db

@app.route('/')
def home():
    return "Flask app is up and running!"

@app.route('/register', methods=['POST'])
def register_number():
    # Hardcoding the values for testing
    org = 'STC'  # Hardcoded organization name
    number = '1234567890'  # Hardcoded phone number

    # Simulate telecom API request to validate the number
    telecom_response = simulate_telecom_api_request(number)

    if telecom_response['status'] == 'error':
        return jsonify(telecom_response), 400

    # Connect to MySQL and insert the data into the database
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO official_numbers (organization_name, phone_number) VALUES (%s, %s)",
            (org, number)
        )
        db.commit()  # Commit the transaction to the database
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
@app.route('/admin', methods=['GET'])
def admin_dashboard():
    # Retrieve unapproved registrations from the database
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM official_numbers WHERE approved = 0")
    registrations = cursor.fetchall()
    cursor.close()
    db.close()

    return jsonify({"registrations": registrations})


# Admin approval route (POST)
@app.route('/admin/approve', methods=['POST'])
def approve_registration():
    data = request.get_json()
    registration_id = data.get('id')

    # Update the status to approved (1)
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE official_numbers SET approved = 1 WHERE id = %s", (registration_id,))
    db.commit()
    cursor.close()
    db.close()

    return jsonify({"message": "Registration approved successfully!"}), 200


# Simulate telecom API request function
def simulate_telecom_api_request(phone_number):
    """
    Simulate a telecom API request (for testing).
    Example: Simulate checking if the phone number is valid.
    """
    if len(phone_number) == 10:  # Simulate a basic length check for phone numbers
        return {"status": "success", "message": "Number is valid"}
    else:
        return {"status": "error", "message": "Invalid number"}


if __name__ == '__main__':
   app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5006)), debug=True)

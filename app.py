from flask import Flask, request, jsonify
from urllib.parse import urlparse
import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
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
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5005)), debug=True)

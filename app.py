from flask import Flask, request, jsonify
import mysql.connector
import os 
import urllib.parse as up

# Initialize the Flask app
app = Flask(__name__)

# Fetch the MySQL URL from environment variables (set this in Railway)
MYSQL_URL = os.getenv("MYSQL_URL")

# Parse the connection details from the URL
result = up.urlparse(MYSQL_URL)

# Ensure port is provided, default to 3306 if missing
port = result.port if result.port else 3306

# Connect to MySQL using the details from the URL
try:
    db = mysql.connector.connect(
        host=result.hostname,    # MySQL Host (mysql-ywzg.railway.internal)
        user=result.username,    # MySQL User (root)
        password=result.password,  # MySQL Password (your password)
        database=result.path[1:],  # Database (railway)
        port=port                # Port (3306)
    )
    print("Successfully connected to MySQL")
except mysql.connector.Error as err:
    print(f"Error: {err}")

# Route to register phone number
@app.route('/register', methods=['POST'])
def register_number():
    data = request.get_json()
    org = data.get('organization')
    number = data.get('number')

    if not org or not number:
        return jsonify({"error": "Missing organization or number"}), 400

    try:
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO official_numbers (organization_name, phone_number) VALUES (%s, %s)",
            (org, number)
        )
        db.commit()
        cursor.close()
        return jsonify({"message": "Number registered successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to look up phone number
@app.route('/lookup', methods=['GET'])
def lookup_number():
    phone_number = request.args.get('number')
    if not phone_number:
        return jsonify({"error": "Missing 'number' parameter"}), 400

    try:
        cursor = db.cursor()
        cursor.execute("SELECT organization_name FROM official_numbers WHERE phone_number = %s", (phone_number,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return jsonify({"organization": result[0]})
        else:
            return jsonify({"message": "Number not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Home route for testing the app
@app.route('/')
def home():
    return '✅ Hello from your live Flask app on Railway!'

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

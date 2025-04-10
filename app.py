from flask import Flask, request, jsonify
import mysql.connector
import os 
import urllib.parse as up
# Fetch the MySQL URL from environment variables
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
        password=result.password,  # MySQL Password (HLXIxafyHNKRCJEbELWAtuxLmbgZmxgs)
        database=result.path[1:],  # Database (railway)
        port=port                # Port (3306)
    )
    print("Successfully connected to MySQL")
except mysql.connector.Error as err:
    print(f"Error: {err}")

app = Flask(__name__)
db = mysql.connector.connect(
    host=os.environ.get("MYSQLHOST"),
    user=os.environ.get("MYSQLUSER"),
    password=os.environ.get("MYSQLPASSWORD"),
    database=os.environ.get("MYSQLDATABASE"),
    port=int(os.environ.get("MYSQLPORT", 3306))
)

@app.route('/')
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

def home():
    return '✅ Hello from your live Flask app on Railway!'
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
# 🔐 Secret API key
API_KEY = "admin123"  # 👈 You can change this to anything you want

# 🔐 Check if request is authorized
def is_authorized(request):
    apikey = request.args.get("apikey")
    return apikey == API_KEY

# 🔌 Connect to MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="6250",  # Change this if you use a password
        database="official_caller_id"
    )

# 🔍 GET /lookup
@app.route('/lookup', methods=['GET'])
def lookup_number():
    phone_number = request.args.get('number')
    if not phone_number:
        return jsonify({"error": "Missing 'number' parameter"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT organization_name FROM registered_numbers WHERE phone_number = %s", (phone_number,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return jsonify({"caller": result[0]})
    else:
        return jsonify({"caller": "Unknown number"})

# 🆕 POST /register
@app.route('/register', methods=['POST'])
@app.route('/lookup', methods=['GET'])
def lookup_number():
    number = request.args.get('number')

    if not number:
        return jsonify({"error": "Missing number parameter"}), 400

    try:
        cursor = db.cursor()
        cursor.execute(
            "SELECT organization_name FROM official_numbers WHERE phone_number = %s",
            (number,)
        )
        result = cursor.fetchone()
        cursor.close()

        if result:
            return jsonify({"organization": result[0]})
        else:
            return jsonify({"message": "Number not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def register_number():
    if not is_authorized(request):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    phone_number = data.get('phone_number')
    organization_name = data.get('organization_name')

    if not phone_number or not organization_name:
        return jsonify({"error": "Missing phone number or organization name"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO registered_numbers (phone_number, organization_name) VALUES (%s, %s)",
            (phone_number, organization_name)
        )
        conn.commit()
    except mysql.connector.Error as err:
        conn.close()
        return jsonify({"error": str(err)}), 500
    finally:
        conn.close()

    return jsonify({"message": "Number registered successfully!"}), 201

# 📋 GET /all
@app.route('/all', methods=['GET'])
def get_all_numbers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, phone_number, organization_name FROM registered_numbers")
    rows = cursor.fetchall()
    conn.close()

    numbers = []
    for row in rows:
        numbers.append({
            "id": row[0],
            "phone_number": row[1],
            "organization_name": row[2]
        })

    return jsonify(numbers)

# 🔁 PUT /update
@app.route('/update', methods=['PUT'])
def update_number():
    if not is_authorized(request):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    phone_number = data.get('phone_number')
    new_name = data.get('organization_name')

    if not phone_number or not new_name:
        return jsonify({"error": "Missing phone number or new organization name"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM registered_numbers WHERE phone_number = %s", (phone_number,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({"error": "Number not found"}), 404

    try:
        cursor.execute(
            "UPDATE registered_numbers SET organization_name = %s WHERE phone_number = %s",
            (new_name, phone_number)
        )
        conn.commit()
    except mysql.connector.Error as err:
        conn.close()
        return jsonify({"error": str(err)}), 500
    finally:
        conn.close()

    return jsonify({"message": "Number updated successfully!"}), 200

# ❌ DELETE /delete
@app.route('/delete', methods=['DELETE'])
def delete_number():
    if not is_authorized(request):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    phone_number = data.get('phone_number')

    if not phone_number:
        return jsonify({"error": "Missing phone number"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM registered_numbers WHERE phone_number = %s", (phone_number,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({"error": "Number not found"}), 404

    try:
        cursor.execute("DELETE FROM registered_numbers WHERE phone_number = %s", (phone_number,))
        conn.commit()
    except mysql.connector.Error as err:
        conn.close()
        return jsonify({"error": str(err)}), 500
    finally:
        conn.close()

    return jsonify({"message": "Number deleted successfully!"}), 200

# 🚀 Start the server
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)


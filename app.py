from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)
@app.route('/')
def home():
    return '✅ Hello from your live Flask app on Railway!'
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


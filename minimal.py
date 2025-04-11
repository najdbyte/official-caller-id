from flask import Flask, request, jsonify

app = Flask(__name__)

# A simple route to test POST method
@app.route('/test_register', methods=['POST'])
def test_register():
    return jsonify({"message": "POST request received!"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)

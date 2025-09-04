from flask import Flask, request, jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/engine_temp_warning_db"
mongo = PyMongo(app)

WARNING_THRESHOLD = 90.0

@app.route('/')
def home():
    return "Engine Temperature Warning API Backend Running"

@app.route('/api/temperature', methods=['POST'])
def receive_temperature():
    try:
        # Force parsing JSON even if content-type is missing or incorrect
        data = request.get_json(force=True)
        if not data or 'temperature' not in data:
            return jsonify({"error": "Temperature value is required"}), 400

        temp = float(data['temperature'])

        mongo.db.temperature_data.insert_one({"temperature": temp})

        warning = temp > WARNING_THRESHOLD

        return jsonify({"temperature": temp, "warning": warning})

    except Exception as e:
        print("Exception in receive_temperature:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

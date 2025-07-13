from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import json_util
import json
import os
from dotenv import load_dotenv

# .env ফাইল থেকে এনভায়রনমেন্ট ভ্যারিয়েবল লোড করা
load_dotenv()

app = Flask(__name__)
CORS(app)

# --- MongoDB Atlas কানেকশন ---
MONGO_CONNECTION_STRING = os.getenv('MONGO_URI')
incidents_collection = None  # ডিফল্টভাবে None সেট করা

if not MONGO_CONNECTION_STRING:
    print("Error: MONGO_URI not found in environment variables.")
else:
    try:
        client = MongoClient(MONGO_CONNECTION_STRING)
        db = client['political_violence_db']
        incidents_collection = db['incidents']
        print("MongoDB connection successful.")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")


@app.route('/api/incidents', methods=['GET'])
def get_incidents():
    # এরর সমাধানের জন্য এই লাইনটি পরিবর্তন করা হয়েছে
    if incidents_collection is None:
        return jsonify({"error": "Database connection not available"}), 500
        
    try:
        # ডেটাবেস থেকে সব ঘটনা খুঁজে বের করা
        incidents = incidents_collection.find({}).sort("incident_date", -1) # তারিখ অনুযায়ী সাজানো
        
        # BSON (MongoDB format) থেকে JSON এ কনভার্ট করা
        response = json.loads(json_util.dumps(incidents))
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

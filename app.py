import os
import io
import json
import sqlite3
from flask import Flask, request, jsonify
from PIL import Image
from google import genai
from google.genai import types

app = Flask(__name__)
DB_NAME = "kyc.db"

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
ai_client = genai.Client()



# --- Database Setup ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kyc_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            dob TEXT,
            id_number TEXT,
            address TEXT,
            document_type TEXT,
            verification_status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()


# --- Gemini Vision KYC Extractor ---
def extract_kyc_data(image_bytes: bytes) -> dict:
    image = Image.open(io.BytesIO(image_bytes))
    
    # Define exact schema for structured output
    schema = {
        "type": "OBJECT",
        "properties": {
            "full_name": {"type": "STRING", "description": "Full name of the person"},
            "dob": {"type": "STRING", "description": "Date of birth in YYYY-MM-DD or standard format"},
            "id_number": {"type": "STRING", "description": "ID or Document identification number"},
            "address": {"type": "STRING", "description": "Full residential address"},
            "document_type": {"type": "STRING", "description": "Type of ID (e.g. Passport, Driver License, National ID, Application Form)"}
        },
        "required": ["full_name", "id_number", "document_type"]
    }

    prompt = (
        "You are an expert KYC document verification assistant. Analyze this document image. "
        "Extract the person's full name, date of birth, ID number, address, and document type. "
        "If handwritten text is present, perform high-precision OCR. "
        "If a field cannot be identified or is missing, set its value to 'NOT_FOUND'."
    )

    response = ai_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[prompt, image],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.1
        )
    )

    return json.loads(response.text)


# --- API Routes ---
@app.route("/api/verify-kyc", methods=["POST"])
def verify_kyc():
    if "file" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files["file"]
    image_bytes = file.read()

    try:
        # Step 1: Extract data via Gemini Vision
        data = extract_kyc_data(image_bytes)

        # Step 2: Validate missing/required fields
        missing_fields = [k for k, v in data.items() if v in [None, "", "NOT_FOUND"]]
        
        status = "PASSED" if not missing_fields else "FLAGGED_FOR_REVIEW"

        # Step 3: Log clean record into SQLite
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO kyc_records (full_name, dob, id_number, address, document_type, verification_status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data.get("full_name", "UNKNOWN"),
            data.get("dob", "UNKNOWN"),
            data.get("id_number", "UNKNOWN"),
            data.get("address", "UNKNOWN"),
            data.get("document_type", "UNKNOWN"),
            status
        ))
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            "record_id": record_id,
            "status": status,
            "missing_fields": missing_fields,
            "extracted_data": data
        }), 200

    except Exception as e:
        return jsonify({"error": f"KYC Processing Failed: {str(e)}"}), 500


@app.route("/api/records", methods=["GET"])
def get_records():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name, dob, id_number, address, document_type, verification_status, created_at FROM kyc_records ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    records = [
        {
            "id": r[0],
            "full_name": r[1],
            "dob": r[2],
            "id_number": r[3],
            "address": r[4],
            "document_type": r[5],
            "status": r[6],
            "created_at": r[7]
        }
        for r in rows
    ]
    return jsonify(records), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
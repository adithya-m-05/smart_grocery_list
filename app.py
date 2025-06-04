# from flask import Flask, request, jsonify, render_template
# import requests
# import os

# app = Flask(__name__)

# # Replace with your actual OCR.space API key
# OCR_API_KEY = 'K84834139488957'

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload():
#     if 'receipt' not in request.files:
#         return jsonify({'error': 'No file part'}), 400

#     file = request.files['receipt']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400

#     # Send image to OCR.space API
#     ocr_url = 'https://api.ocr.space/parse/image'
#     payload = {
#         'apikey': OCR_API_KEY,
#         'language': 'eng',
#         'isTable': True
#     }
#     files = {
#         'file': (file.filename, file.stream, file.mimetype)
#     }

#     response = requests.post(ocr_url, data=payload, files=files)
#     result = response.json()

#     if result.get('IsErroredOnProcessing'):
#         return jsonify({'error': result.get('ErrorMessage', 'OCR processing error')}), 500

#     parsed_text = result['ParsedResults'][0]['ParsedText']
#     items = parse_items(parsed_text)

#     return jsonify({'items': items})

# def parse_items(text):
#     """
#     Parses the OCR-extracted text to identify grocery items.
#     This is a simplistic parser and may need enhancements for complex receipts.
#     """
#     lines = text.split('\n')
#     items = []
#     for line in lines:
#         line = line.strip()
#         if not line:
#             continue
#         # Basic heuristic: lines with alphabets and numbers
#         if any(char.isalpha() for char in line) and any(char.isdigit() for char in line):
#             items.append(line)
#     return items

# if __name__ == '__main__':
#     app.run(debug=True)

#first code above

# from flask import Flask, render_template, request, jsonify
# import requests
# import os

# app = Flask(__name__)

# # Replace this with your actual OCR.Space API Key
# OCR_API_KEY = 'K85024854288957'  # 🔑 REQUIRED

# # Recommendations Map
# RECOMMENDATION_MAP = {
#     'milk': ['cereal', 'cookies'],
#     'bread': ['butter', 'jam'],
#     'rice': ['lentils', 'spices'],
#     'eggs': ['cheese', 'bread'],
#     'banana': ['milk', 'peanut butter'],
#     'coffee': ['sugar', 'milk'],
# }

# # Recommend items based on scanned content
# def recommend_items(items):
#     recommendations = set()
#     for item in items:
#         item_lower = item.lower()
#         for key in RECOMMENDATION_MAP:
#             if key in item_lower:
#                 recommendations.update(RECOMMENDATION_MAP[key])
#     return list(recommendations)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload():
#     if 'receipt' not in request.files:
#         return jsonify({'error': 'No file uploaded'})

#     file = request.files['receipt']

#     # Check for allowed image types
#     if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
#         return jsonify({'error': 'Unsupported file type. Please upload JPG or PNG.'})

#     # OCR API call
#     try:
#         response = requests.post(
#             'https://api.ocr.space/parse/image',
#             files={'filename': (file.filename, file.stream, file.mimetype)},
#             data={'apikey': OCR_API_KEY, 'language': 'eng'}
#         )

#         result = response.json()
#         if result.get('IsErroredOnProcessing', False):
#             error_msg = result.get('ErrorMessage', ['Unknown OCR error'])[0]
#             return jsonify({'error': f'OCR failed: {error_msg}'})

#         parsed_text = result['ParsedResults'][0]['ParsedText']
#         lines = parsed_text.split('\n')
#         items = [line.strip() for line in lines if line.strip()]
#         recommendations = recommend_items(items)

#         return jsonify({'items': items, 'recommendations': recommendations})
#     except Exception as e:
#         return jsonify({'error': f'Failed to parse receipt. {str(e)}'})

# if __name__ == '__main__':
#     app.run(debug=True)

#above is 2nd code

import os
import uuid
import sqlite3
import pandas as pd
from flask import Flask, request, jsonify, render_template
from PIL import Image
import google.generativeai as genai
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB_PATH = 'grocery.db'
EXCEL_PATH = 'receipts.xlsx'

# Gemini API key
genai.configure(api_key="AIzaSyAU_TMouKpdwVxr6e01Km9VrtZtAi1YpSs")
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# Setup DB
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS grocery_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT,
                price REAL,
                timestamp TEXT
            )
        ''')
init_db()

# Recommendations
RECOMMENDATION_MAP = {
    'milk': ['cereal', 'cookies'],
    'bread': ['butter', 'jam'],
    'rice': ['lentils', 'spices'],
    'eggs': ['cheese', 'bread'],
    'banana': ['milk', 'peanut butter'],
    'coffee': ['sugar', 'milk'],
}

def recommend_items(items):
    recommendations = set()
    for item in items:
        for key in RECOMMENDATION_MAP:
            if key in item.lower():
                recommendations.update(RECOMMENDATION_MAP[key])
    return list(recommendations)

def save_to_db_and_excel(items):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = []

    with sqlite3.connect(DB_PATH) as conn:
        for item in items:
            parts = item.rsplit(' ', 1)
            name = parts[0].strip()
            price = float(parts[1]) if len(parts) > 1 and parts[1].replace('.', '', 1).isdigit() else 0.0
            conn.execute("INSERT INTO grocery_items (item, price, timestamp) VALUES (?, ?, ?)",
                         (name, price, timestamp))
            rows.append({'Item': name, 'Price': price, 'Timestamp': timestamp})

    # Append to Excel
    df = pd.DataFrame(rows)
    if os.path.exists(EXCEL_PATH):
        old_df = pd.read_excel(EXCEL_PATH)
        df = pd.concat([old_df, df], ignore_index=True)
    df.to_excel(EXCEL_PATH, index=False)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload():
    if 'receipt' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['receipt']
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        return jsonify({'error': 'Unsupported file type'}), 400

    filename = str(uuid.uuid4()) + "_" + file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        image = Image.open(filepath)
        prompt = (
            "You're a smart assistant. Extract only grocery items with price from this receipt image. "
            "Return the result in the format: 'ItemName Price'. Ignore tax, total, discounts, etc."
        )
        response = model.generate_content([prompt, image])
        result = response.text.strip().split('\n')
        items = [line.strip() for line in result if line.strip()]

        save_to_db_and_excel(items)
        recommendations = recommend_items(items)

        return jsonify({'items': items, 'recommendations': recommendations})

    except Exception as e:
        return jsonify({'error': 'Gemini processing failed', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)



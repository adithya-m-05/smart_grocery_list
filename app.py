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

from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# Replace this with your actual OCR.Space API Key
OCR_API_KEY = 'K85024854288957'  # 🔑 REQUIRED

# Recommendations Map
RECOMMENDATION_MAP = {
    'milk': ['cereal', 'cookies'],
    'bread': ['butter', 'jam'],
    'rice': ['lentils', 'spices'],
    'eggs': ['cheese', 'bread'],
    'banana': ['milk', 'peanut butter'],
    'coffee': ['sugar', 'milk'],
}

# Recommend items based on scanned content
def recommend_items(items):
    recommendations = set()
    for item in items:
        item_lower = item.lower()
        for key in RECOMMENDATION_MAP:
            if key in item_lower:
                recommendations.update(RECOMMENDATION_MAP[key])
    return list(recommendations)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'receipt' not in request.files:
        return jsonify({'error': 'No file uploaded'})

    file = request.files['receipt']

    # Check for allowed image types
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        return jsonify({'error': 'Unsupported file type. Please upload JPG or PNG.'})

    # OCR API call
    try:
        response = requests.post(
            'https://api.ocr.space/parse/image',
            files={'filename': (file.filename, file.stream, file.mimetype)},
            data={'apikey': OCR_API_KEY, 'language': 'eng'}
        )

        result = response.json()
        if result.get('IsErroredOnProcessing', False):
            error_msg = result.get('ErrorMessage', ['Unknown OCR error'])[0]
            return jsonify({'error': f'OCR failed: {error_msg}'})

        parsed_text = result['ParsedResults'][0]['ParsedText']
        lines = parsed_text.split('\n')
        items = [line.strip() for line in lines if line.strip()]
        recommendations = recommend_items(items)

        return jsonify({'items': items, 'recommendations': recommendations})
    except Exception as e:
        return jsonify({'error': f'Failed to parse receipt. {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)

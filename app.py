from flask import Flask, request, jsonify
import pandas as pd
import requests
from io import BytesIO
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from a .env file if it exists
load_dotenv()

# Get the URL of the Excel file from the environment variable
EXCEL_URL = os.getenv('EXCEL_URL')

if not EXCEL_URL:
    raise ValueError("No EXCEL_URL set for Flask application. Set the EXCEL_URL environment variable.")

def download_excel(url):
    response = requests.get(url)
    response.raise_for_status()  # Ensure we notice bad responses
    return BytesIO(response.content)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    column = request.args.get('column', '')

    if not query or not column:
        return jsonify({'error': 'Query and column parameters are required.'}), 400

    # Load the Excel file into a DataFrame
    excel_data = download_excel(EXCEL_URL)
    df = pd.read_excel(excel_data)

    if column not in df.columns:
        return jsonify({'error': f'Column {column} does not exist in the Excel file.'}), 400

    # Perform the search
    results = df[df[column].astype(str).str.contains(query, case=False, na=False)]

    return jsonify(results.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)

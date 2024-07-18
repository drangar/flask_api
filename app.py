from flask import Flask, request, jsonify
import pandas as pd
import requests
from io import BytesIO

app = Flask(__name__)

# URL of the Excel file
EXCEL_URL = 'https://ibm.box.com/shared/static/brx199pxik47jizxka9pdy4563084tuw.xlsx'

def download_excel(url):
    response = requests.get(url)
    response.raise_for_status()  # Ensure we notice bad responses
    return BytesIO(response.content)

@app.route('/search', methods=['GET'])
def search():

    # Load the Excel file into a DataFrame
    excel_data = download_excel(EXCEL_URL)
    df = pd.read_excel(excel_data)

    name_query = request.args.get('name', '')
    title_query = request.args.get('title', '')
    country_query = request.args.get('country', '')

    mask = pd.Series([True] * len(df))

    if name_query:
        mask &= df['name'].astype(str).str.contains(name_query, case=False, na=False)
    if title_query:
        mask &= df['title'].astype(str).str.contains(title_query, case=False, na=False)
    if country_query:
        mask &= df['country'].astype(str).str.contains(country_query, case=False, na=False)

    results = df[mask]

    return jsonify(results.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)

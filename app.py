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
    queries = request.args.getlist('query')
    columns = request.args.getlist('column')

    if not queries or not columns or len(queries) != len(columns):
        return jsonify({'error': 'Query and column parameters are required, and their lengths must match.'}), 400

    # Load the Excel file into a DataFrame
    excel_data = download_excel(EXCEL_URL)
    df = pd.read_excel(excel_data)

    # Check if the columns exist in the DataFrame
    for column in columns:
        if column not in df.columns:
            return jsonify({'error': f'Column {column} does not exist in the Excel file.'}), 400

    # Perform the search for each query-column pair
    mask = pd.Series([True] * len(df))
    for query, column in zip(queries, columns):
        mask &= df[column].astype(str).str.contains(query, case=False, na=False)

    results = df[mask]

    return jsonify(results.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)

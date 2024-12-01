from flask import Flask, request, jsonify, send_from_directory
import os
from database import init_db, get_order_by_place_gov, insert_order, update_order ,get_pending_orders , get_completed_orders
from services import generate_order_id, save_json_file, check_order_status_or_create
from config import DATA_DIR
import json
from time import time

app = Flask(__name__)

# Initialize the database
init_db()

@app.route('/place_order', methods=['POST'])
def place_order():
    """Place new orders or check the status of existing orders."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # List of place and gov names
    places_and_govs = data.get('places_and_govs')

    if not places_and_govs or not isinstance(places_and_govs, list):
        return jsonify({'error': 'Invalid input: places_and_govs must be a list'}), 400

    results = []

    # Process each place-governorate pair
    for place_gov in places_and_govs:
        place_name = place_gov.get('place_name')
        gov_name = place_gov.get('gov_name')

        if not place_name or not gov_name:
            results.append({
                'place_name': place_name,
                'gov_name': gov_name,
                'status': 'Invalid place or gov name'
            })
            continue

        # Check if the order exists in the database and process it
        order_result = check_order_status_or_create(place_name, gov_name)

        results.append({
            'place_name': place_name,
            'gov_name': gov_name,
            'status': order_result['status'],
            'order_id': order_result.get('order_id'),
            'file_url': order_result.get('file_url')
        })

    return jsonify({'results': results}), 200


@app.route('/upload_json', methods=['POST'])
def upload_json():
    """Upload the JSON file for a place and governorate."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Check if the file is a valid JSON
    if not file.filename.endswith('.json'):
        return jsonify({'error': 'Invalid file type. Only JSON files are allowed'}), 400

    # Extract place_name and gov_name from the filename
    try:
        # Split filename (excluding the extension) by '_'
        filename = file.filename.rsplit('.', 1)[0]  # Remove the file extension
        place_name, gov_name = filename.split('_', 1)  # Split by first underscore

        # Ensure that both place_name and gov_name are valid
        if not place_name or not gov_name:
            return jsonify({'error': 'Invalid file name format. Expected "place_name_governorate.json"'}), 400

        # Save the file
        file_path = save_json_file(file, place_name, gov_name)

        url = f'https://geoegyBackend.pythonanywhere.com/get_data/{place_name}/{gov_name}'

        # Update the order status in the database
        update_order_status(place_name, gov_name, url)

        return jsonify({'message': 'File uploaded successfully', 'file_url': file_path}), 200

    except ValueError:
        return jsonify({'error': 'Invalid file name format. Could not extract place_name and gov_name'}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to parse the file: {str(e)}'}), 400



@app.route('/get_data/<place_name>/<gov_name>', methods=['GET'])
def get_data(place_name, gov_name):
    """Serve the JSON file for a given place and governorate."""
    try:
        directory = os.path.join(DATA_DIR, place_name, gov_name)
        return send_from_directory(directory, f'{place_name}_{gov_name}.json', as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to serve file: {str(e)}'}), 500


@app.route('/get_pending_orders', methods=['GET'])
def get_pending():
    """Get all pending orders."""
    try:
        # Get all pending orders from the database
        pending_orders = get_pending_orders()

        # If no pending orders exist
        if not pending_orders:
            return jsonify({'message': 'No pending orders found'}), 200

        # Format the response
        orders_response = []
        for order in pending_orders:
            orders_response.append({
                'order_id': order[0],
                'place_name': order[1],
                'gov_name': order[2],
                'status': order[3],
                'created_at': order[4],
                'file_url': order[5]
            })

        return jsonify({'pending_orders': orders_response}), 200

    except Exception as e:
        return jsonify({'error': f'Failed to retrieve pending orders: {str(e)}'}), 500
    

@app.route('/get_completed_orders', methods=['GET'])
def get_completed():
    """Get all completed orders."""
    try:
        # Get all pending orders from the database
        completed_orders = get_completed_orders()

        # If no pending orders exist
        if not completed_orders:
            return jsonify({'message': 'No pending orders found'}), 200

        # Format the response
        orders_response = []
        for order in completed_orders:
            orders_response.append({
                'order_id': order[0],
                'place_name': order[1],
                'gov_name': order[2],
                'status': order[3],
                'created_at': order[4],
                'file_url': order[5]
            })

        return jsonify({'completed_orders': orders_response}), 200

    except Exception as e:
        return jsonify({'error': f'Failed to retrieve completed orders: {str(e)}'}), 500


def update_order_status(place_name, gov_name, file_path):
    """Update the order status and file URL in the database."""
    order = get_order_by_place_gov(place_name, gov_name)

    if order:
        # Update existing order if found
        update_order(order[0][0], 'completed', file_path)
    else:
        # Create a new order if not found
        new_order = {
            'order_id': generate_order_id(),
            'place_name': place_name,
            'gov_name': gov_name,
            'status': 'completed',
            'created_at': int(time()),
            'file_url': file_path
        }
        insert_order(new_order)




if __name__ == '__main__':
    app.run(debug=True, port=5050, use_reloader=False)

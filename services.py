import os
from database import get_order_by_place_gov ,insert_order ,update_order
from config import DATA_DIR
import uuid
from time import time  # Correct import for the time function

def generate_order_id():
    """Generate a unique order ID."""
    return str(uuid.uuid4())

def save_json_file(file, place_name, gov_name):
    """Save the uploaded JSON file and return its path. If a file with the same name exists, keep the largest one."""
    # Define the path to save the file
    directory = os.path.join(DATA_DIR, place_name, gov_name)
    os.makedirs(directory, exist_ok=True)

    # Secure the file name
    filename = f'{place_name}_{gov_name}.json'
    file_path = os.path.join(directory, filename)

    # Check if the file already exists
    if os.path.exists(file_path):
        # Get the size of the existing file and the new uploaded file
        existing_file_size = os.path.getsize(file_path)
        new_file_size = len(file.read())  # Get size of the uploaded file

        # Reset the file pointer after reading the file size
        file.seek(0)

        # Compare file sizes and keep the largest one
        if new_file_size > existing_file_size:
            # If the new file is larger, replace the old file
            os.remove(file_path)
            file.save(file_path)
        else:
            # If the existing file is larger or same size, don't replace
            return file_path
    else:
        # If the file doesn't exist, just save the new file
        file.save(file_path)

    return file_path



def check_order_status_or_create(place_name, gov_name):
    """Check if the order exists and update based on file availability."""
    try:
        file_path = os.path.join(DATA_DIR, place_name, gov_name, f'{place_name}_{gov_name}.json')

        # Check if the file exists
        file_exists = os.path.exists(file_path)
        
        # Check if the order already exists in the database
        order = get_order_by_place_gov(place_name, gov_name)

        url = f'https://geoegyBackend.pythonanywhere.com/get_data/{place_name}/{gov_name}'


        if order:
            # If the order exists and the file exists, mark the order as 'completed'
            if file_exists:
                update_order(order[0][0], status='completed', file_url=url)
                return {
                    'order_id': order[0][0],
                    'place_name': order[0][1],
                    'gov_name': order[0][2],
                    'status': 'completed',
                    'created_at': order[0][4],
                    'file_url': url
                }
            else:
                # If the file doesn't exist, keep it as 'pending' or 'processing'
                return {
                    'order_id': order[0][0],
                    'place_name': order[0][1],
                    'gov_name': order[0][2],
                    'status': 'pending',  # You can set this to 'pending' if required
                    'created_at': order[0][4],
                    'file_url': None
                }
        else:
            # If the order doesn't exist, create a new order
            if file_exists:
                new_order = {
                    'order_id': generate_order_id(),
                    'place_name': place_name,
                    'gov_name': gov_name,
                    'status': 'completed',  # Status is 'completed' because the file exists
                    'created_at': int(time()),
                    'file_url': url
                }
            else:
                new_order = {
                    'order_id': generate_order_id(),
                    'place_name': place_name,
                    'gov_name': gov_name,
                    'status': 'pending',  # Status is 'pending' as no file exists yet
                    'created_at': int(time()),
                    'file_url': None
                }

            insert_order(new_order)
            return new_order

    except Exception as e:
        raise RuntimeError(f"Failed to check or create order: {e}")


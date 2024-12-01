import os
import sys

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Function to safely create directories, ensuring compatibility with Arabic and English folder names
def create_dir(directory_path):
    try:
        os.makedirs(directory_path, exist_ok=True)
        print(f"Directory created or already exists: {directory_path}")
    except Exception as e:
        print(f"Error creating directory {directory_path}: {str(e)}")
        sys.exit(1)

# Directory to store generated data (supports Arabic and English names)
DATA_DIR = os.path.join(BASE_DIR, 'data')  # You can replace 'data' with an Arabic name, e.g., 'بيانات'
create_dir(DATA_DIR)

# Database configuration
DATABASE = os.path.join(BASE_DIR, 'orders.db')

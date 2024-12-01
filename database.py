import sqlite3
import os
from config import DATABASE

def init_db():
    """Initialize the database and create the orders table."""
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                place_name TEXT NOT NULL,
                gov_name TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                file_url TEXT
            )
        ''')
        conn.commit()
        conn.close()

def insert_order(order_data):
    """Insert a new order into the database."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (order_id, place_name, gov_name, status, created_at, file_url)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        order_data['order_id'],
        order_data['place_name'],
        order_data['gov_name'],
        order_data['status'],
        order_data['created_at'],
        order_data['file_url']
    ))
    conn.commit()
    conn.close()

    print(f"Order inserted: {order_data}")  # Debugging log


def update_order(order_id, status, file_url=None):
    """Update an existing order."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    if file_url:
        cursor.execute('''
            UPDATE orders SET status = ?, file_url = ? WHERE order_id = ?
        ''', (status, file_url, order_id))
    else:
        cursor.execute('''
            UPDATE orders SET status = ? WHERE order_id = ?
        ''', (status, order_id))
    conn.commit()
    conn.close()

def get_order_by_place_gov(place_name, gov_name):
    """Retrieve an order by place_name and gov_name."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM orders WHERE place_name = ? AND gov_name = ?
    ''', (place_name, gov_name))
    orders = cursor.fetchall()
    conn.close()
    return orders

def get_pending_orders():
    """Retrieve all orders with the status 'pending'."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT order_id, place_name, gov_name, status, created_at, file_url
        FROM orders WHERE status = 'pending'
    ''')
    pending_orders = cursor.fetchall()
    conn.close()
    return pending_orders

def get_completed_orders():
    """Retrieve all orders with the status 'completed'."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT order_id, place_name, gov_name, status, created_at, file_url
        FROM orders WHERE status = 'completed'
    ''')
    completed_orders = cursor.fetchall()
    conn.close()
    return completed_orders

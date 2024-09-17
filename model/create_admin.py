import sqlite3
import bcrypt
from pathlib import Path

# Function to hash a password using bcrypt
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

# Function to create an admin user in the database
def create_admin():
    db_path = 'face.db'
    
    try:
        # Connect to SQLite database with a timeout to handle database lock issues
        with sqlite3.connect(db_path, timeout=10) as conn:
            cursor = conn.cursor()

            # Create users table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
            ''')

            # Check if the admin user already exists
            cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
            if cursor.fetchone()[0] > 0:
                print("Admin user already exists.")
                return

            # Define the admin username and password
            username = 'admin'
            password = 'Admin12345'
            hashed_password = hash_password(password)

            # Insert the admin user with the hashed password
            cursor.execute('''
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
            ''', (username, hashed_password))

            conn.commit()
            print("Admin user created successfully.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    create_admin()


from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import re
from Crypto.Cipher import AES
import base64

# Create a Flask web application
app = Flask(__name__)

# AES secret key for encrypting passwords 
SECRET_KEY = b'12345678901234567890123456789012'

# Helper function to pad text so it's a multiple of 16 bytes
def pad(text):
    while len(text) % 16 != 0:
        text += ' '
    return text

# Function to encrypt a password using AES encryption
def encrypt_password(password):
    cipher = AES.new(SECRET_KEY, AES.MODE_ECB)
    padded_password = pad(password)  # Ensure password length is correct
    encrypted_bytes = cipher.encrypt(padded_password.encode())
    return base64.b64encode(encrypted_bytes).decode('utf-8')  # Return as a string

# Function to create and initialize the database
def init_db():
    conn = sqlite3.connect("sandmannDB.db")  # Connect to SQLite database
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS users") # Delete the users table if it already exists
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """) # Create a new users table
    # Insert some sample users with encrypted passwords
    users = [
        ('user1', encrypt_password('password123')),
        ('admin', encrypt_password('adminpass')),
        ('user2', encrypt_password('pass123')),
        ('user3', encrypt_password('zs12!'))
    ]
    cursor.executemany("INSERT INTO users (username, password) VALUES (?, ?)", users)
    conn.commit()
    conn.close()

# Initialize the database once when the server starts
init_db()

# Define the home page route 
@app.route('/')
def home():
    return redirect(url_for('login'))

# Define the login page route
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''            # Message to show on the page (e.g., login success/failure)
    users = None            
    

    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']

        # Input Validation for username
        if not re.match(r'^[A-Za-z0-9_]{3,30}$', username):
            message = "Invalid username format. Only letters, numbers, and underscores allowed (3-30 characters)."
            return render_template('login.html', message=message, users=None)

        # Input Validation for password
        if not (6 <= len(password) <= 50):
            message = "Password must be between 6 and 50 characters."
            return render_template('login.html', message=message, users=None)

        # Connect to database
        conn = sqlite3.connect('sandmannDB.db')
        cursor = conn.cursor()

        # Safe parameterized query changed from the vulnerable version
        query = "SELECT * FROM users WHERE username = ? AND password = ?"

        try:
            # Execute query with parameters
            cursor.execute(query, (username, encrypt_password(password)))
            user = cursor.fetchone()  # Fetch the first matching user, if any

            if user:
                message = f"Welcome, {user[1]}!"  
            else:
                message = "Invalid credentials."  
        except Exception as e:
            message = f"Error occurred: {str(e)}" 

        conn.close()  # Always close the database connection

    # Render the login page with the message
    return render_template('login.html', message=message, users=users)

# Run the app in debug mode (good for development)
if __name__ == '__main__':
    app.run(debug=True)

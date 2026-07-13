from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from Crypto.Cipher import AES
import base64

# Create a Flask web application
app = Flask(__name__)

# AES secret key 
SECRET_KEY = b'12345678901234567890123456789012'

# Function to pad the text so its length is a multiple of 16 
def pad(text):
    while len(text) % 16 != 0:
        text += ' '
    return text

# Function to encrypt a password using AES encryption
def encrypt_password(password):
    cipher = AES.new(SECRET_KEY, AES.MODE_ECB)
    padded_password = pad(password)
    encrypted_bytes = cipher.encrypt(padded_password.encode())
    return base64.b64encode(encrypted_bytes).decode('utf-8')

# Initialize the database with a users table and insert sample users
def init_db():
    conn = sqlite3.connect("sandmannDB.db") # Connect to SQLite database
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS users")  # Delete the users table if it already exists
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)  # Create a new users table
    # Sample user entries with encrypted passwords
    users = [
        ('user1', encrypt_password('password123')),
        ('admin', encrypt_password('adminpass')),
        ('user2', encrypt_password('pass123')),
        ('user3', encrypt_password('zs12!'))
    ]
    cursor.executemany("INSERT INTO users (username, password) VALUES (?, ?)", users)
    conn.commit()
    conn.close()

# Call init_db() once when the app starts to set up the database
init_db()

# Home route redirects to the login page
@app.route('/')
def home():
    return redirect(url_for('login'))

# Login route handles both GET (show form) and POST (process login)
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = '' # Message to show on the page (e.g., login success/failure)
    users = None 
    show_users_table = False  # Controls whether to display the users table

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('sandmannDB.db')
        cursor = conn.cursor()

        # Build the query with user input directly vulnerable to SQL injection
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{encrypt_password(password)}'"

        print("[DEBUG] Executing query:", query)

        try:
            cursor.executescript(query)  # Executes the query that allows multiple statements 

            # After executescript, re-run a safe SELECT to fetch the login user
            cursor.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{encrypt_password(password)}'")
            user = cursor.fetchone()

            if user:
                message = f"Welcome, {user[1]}!"
                # If the username contains 'union', show the full users table
                if 'union' in username.lower():
                    cursor.execute("SELECT * FROM users")
                    users = cursor.fetchall()
                    show_users_table = True
            else:
                message = "Invalid credentials."
        except Exception as e:
            message = f"Error occurred: {str(e)}"

        conn.close()

    return render_template('login.html', message=message, users=users, show_users_table=show_users_table)

# Run the app in debug mode 
if __name__ == '__main__':
    app.run(debug=True)

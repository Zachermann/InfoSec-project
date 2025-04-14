from flask import Flask, render_template, request
import sqlite3
import hashlib

app = Flask(__name__)
DB_NAME = 'sandmannDB.sqlite'

# Initialize the DB and add test users
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    # Add some sample users
    sample_users = [
        ('admin', hashlib.sha256('admin123'.encode()).hexdigest()),
        ('bob', hashlib.sha256('password'.encode()).hexdigest()),
        ('alice', hashlib.sha256('123456'.encode()).hexdigest())
    ]
    for user in sample_users:
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", user)
        except:
            continue
    conn.commit()
    conn.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            # Vulnerable INSERT using f-string
            c.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{hashed_pw}')")
            conn.commit()
            message = "Registration successful."
        except sqlite3.IntegrityError:
            message = "Username already exists."
        conn.close()
        return message + ' <a href="/login">Login</a>'
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        #VULNERABLE login query
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{hashed_pw}'"
        print("Executing query:", query)  # For debugging
        c.execute(query)
        result = c.fetchone()
        conn.close()

        if result:
            return f"Welcome, {username}!"
        else:
            return "Login failed. <a href='/login'>Try again</a>"
    
    return render_template('login.html')

@app.route('/')
def home():
    return "<h2>Welcome!</h2><a href='/register'>Register</a> | <a href='/login'>Login</a>"

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

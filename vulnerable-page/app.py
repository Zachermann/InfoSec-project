from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)
DB_NAME = 'SandmannDB.sqlite'

@app.route('/')
def index():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # WARNING: Plaintext (Phase 1)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')")
            conn.commit()
        except sqlite3.IntegrityError:
            return "Username already exists!"
        finally:
            conn.close()
        
        return "Registration successful. <a href='/login'>Login here</a>"

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'")
        user = c.fetchone()
        conn.close()

        if user:
            return f"Welcome, {username}!"
        else:
            return "Login failed. <a href='/login'>Try again</a>"

    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)

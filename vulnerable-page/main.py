import sqlite3

# create empty database
connection = sqlite3.connect("SandmannDB.db")
# communicate with the database
cursor = connection.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, password TEXT NOT NULL)")

connection.commit()
connection.close()

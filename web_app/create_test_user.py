import sqlite3
import bcrypt
import os

# Ensure instance folder exists
os.makedirs('instance', exist_ok=True)

email = "demo@example.com"
password = "demo123"
username = "demouser"

hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

conn = sqlite3.connect('instance/mental_health.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP,
        last_login TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )
''')

cursor.execute("SELECT * FROM user WHERE email = ?", (email,))
if not cursor.fetchone():
    cursor.execute('''
        INSERT INTO user (username, email, password_hash, created_at)
        VALUES (?, ?, ?, datetime('now'))
    ''', (username, email, hashed.decode('utf-8')))
    print("✅ Demo user created successfully!")
    print("   Email: demo@example.com")
    print("   Password: demo123")
else:
    print("Demo user already exists!")

conn.commit()
conn.close()
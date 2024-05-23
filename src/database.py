import sqlite3

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS roles (
                 id INTEGER PRIMARY KEY,
                 role_name TEXT UNIQUE NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY,
                 username VARCHAR(20) UNIQUE NOT NULL,
                 password VARCHAR(30) NOT NULL,
                 email VARCHAR(20) UNIQUE NOT NULL,
                 celular VARCHAR(20) UNIQUE NOT NULL,
                 role_id INTEGER,
                 face_data BLOB,
                 FOREIGN KEY(role_id) REFERENCES roles(id))''')
    conn.commit()
    conn.close()

def add_role(role_name):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT INTO roles (role_name) VALUES (?)', (role_name,))
    conn.commit()
    conn.close()

def add_user(username, password, email,celular, role_id, face_data):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (username, password, email, celular, role_id, face_data) VALUES (?, ?, ?, ?, ?,?)',
              (username, password, email,celular, role_id, face_data))
    conn.commit()
    conn.close()

def get_user(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return user

def get_role(role_name):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM roles WHERE role_name = ?', (role_name,))
    role = c.fetchone()
    conn.close()
    return role

def get_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    users = c.fetchall()
    conn.close()
    return users

def get_role_user(role_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM roles WHERE id = ?', (role_id,))
    role = c.fetchone()
    conn.close()
    return role


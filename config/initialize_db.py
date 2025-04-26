import os
import sqlite3

base_dir = os.path.dirname(__file__)
db_dir = os.path.abspath(os.path.join(base_dir, '../db'))
db_path = os.path.join(db_dir, 'zoho_database.db')

os.makedirs(db_dir, exist_ok=True)

connection = sqlite3.connect(db_path)
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS new_clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    consent BOOL NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS existing_clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS experts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    qualification TEXT,
    past_companies TEXT,
    country TEXT,
    areas_of_expertise TEXT,
    years_of_experience INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

connection.commit()
connection.close()
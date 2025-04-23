import sqlite3

# Connect to the zoho_expert_matching_agents database
connection = sqlite3.connect('db/zoho_expert_matching_agents.db')
cursor = connection.cursor()

# Create new_clients table
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

connection.commit()
connection.close()

import sqlite3
import uuid

def insert_client(name, email, phone):

    client_id = str(uuid.uuid4())

    conn = sqlite3.connect('db/zoho_database.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO clients (client_id, name, email, phone)
        VALUES (?, ?, ?, ?)
    ''', (client_id, name, email, phone))

    conn.commit()
    conn.close()

    print(f"New client inserted with client_id: {client_id}")

insert_client(
    name="Faiz Raza",
    email="muhammad.faiz@dataropes.ai",
    phone="1234567890"
)

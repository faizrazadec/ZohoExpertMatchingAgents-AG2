import os
import sqlite3
import json
from .utils import is_valid_email, is_valid_phone_number, generate_id, generate_temp_id

from config.config import DB_PATH
from logger.custom_logger import setup_logger

log = setup_logger()

def retrieve_experts():
    log.info("Retrieving experts from database...")
    try:
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            log.info("Connected to database successfully.")

            cursor.execute("SELECT * FROM experts")
            column_names = [description[0] for description in cursor.description]
            experts = cursor.fetchall()
            log.info("Experts retrieved successfully.")
            return [dict(zip(column_names, row)) for row in experts]
    
    except sqlite3.Error as e:
        log.error("Failed to retrieve experts: %s", e)
        return {"status": "error", "message": str(e), "code": 500}
    
    except Exception as e:
        log.error("Unexpected error: %s", e)
        return {"status": "error", "message": str(e), "code": 500}
    
def add_visitor(name: str, email: str, phone: str, consent: bool):
    log.info("Adding new visitor: %s with email: %s and phone: %s", name, email, phone)
    
    if not is_valid_email(email):
        log.critical("Process: Adding visitor aborted.")
        return None
    
    if not is_valid_phone_number(phone):
        log.critical("Process: Adding visitor aborted.")
        return None
    
    visitor_id = generate_id(email, phone)
    temp_id = generate_temp_id(email)

    try:
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            log.info("Connected to database successfully.")
            
            cursor.execute("INSERT INTO visitors (visitor_id, name, email, phone, consent) VALUES (?, ?, ?, ?, ?)",
                        (visitor_id, name, email, phone, int(consent)))
            connection.commit()
            log.info("Visitor added successfully.")

            cursor.execute("UPDATE chat_history SET user_id = ? WHERE user_id = ?", (visitor_id, temp_id))
            connection.commit()

            os.environ["FLAG"] = 'false'
            os.environ["USER_ID"] = visitor_id

            return json.dumps({"status": "success", "code": 200})
    
    except sqlite3.IntegrityError as e:
        log.error(f"Visitor already exists: {e}")
        return json.dumps({"status": "error", "message": "Visitor already exists", "code": 409})
    
    except Exception as e:
        log.error(f"Error adding visitor: {e}")
        return json.dumps({"status": "error", "message": str(e), "code": 500})

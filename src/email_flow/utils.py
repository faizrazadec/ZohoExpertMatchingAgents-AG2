import uuid
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
import sqlite3
import json
import os

from logger.custom_logger import setup_logger

log = setup_logger()

def is_valid_email(email: str) -> bool:
    log.info(f"Validating email: {email}")
    try:
        validate_email(email)
        log.info(f"Email {email} is valid.")
        return True
    except EmailNotValidError:
        log.error(f"Email {email} is not valid.")
        return False
    
def is_valid_phone_number(phone: str) -> bool:
    log.info(f"Validating phone number: {phone}")
    try:
        parsed_number = phonenumbers.parse(phone, None)
        phonenumbers.is_valid_number(parsed_number)
        log.info(f"Phone number {phone} is valid.")
        return True
    except NumberParseException:
        log.error(f"Phone number {phone} is not valid.")
        return False

def generate_id(email: str, phone: str) -> str:
    log.info(f"Generating ID for email: {email} and phone: {phone}")
    if is_valid_email(email) and is_valid_phone_number(phone):
        try:
            name = f"{email}-{phone}"
            id = str(uuid.uuid5(uuid.NAMESPACE_DNS, name))
            log.info(f"Generated ID: {id}")
            return id
        except Exception as e:
            log.error(f"Error generating ID: {e}")
            return None
    else:
        log.error(f"Invalid email or phone number provided.")
        return None
    
def authenticate_client(DB_PATH, email: str) -> int | None:
    log.info(f"Authenticating user with email: {email}")
    
    if not is_valid_email(email):
        log.critical("Authentication aborted.")
        return None

    try:
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            log.info("Connected to database successfully.")
            
            cursor.execute("SELECT client_id FROM clients WHERE email = ?", (email,))
            result = cursor.fetchone()
            
            if result:
                client_id = result[0]
                log.info("Authentication successful. Client ID: %s", client_id)
                return client_id
            else:
                log.warning("Authentication failed. Email not found.")
                return None
    
    except Exception as e:
        log.error(f"Error during authentication: {e}")
        return None

def generate_temp_id(input_value: str) -> str:
    log.info(f"Generating ID for input value: {input_value}")
    
    if "@" in input_value:
        if not is_valid_email(input_value):
            log.error(f"Invalid email provided.")
            return None
    else:
        if not is_valid_phone_number(input_value):
            log.error(f"Invalid phone number provided.")
            return None
    
    try:
        id = str(uuid.uuid5(uuid.NAMESPACE_DNS, input_value))
        log.info(f"Generated ID: {id}")
        return id
    except Exception as e:
        log.error(f"Error generating ID: {e}")
        return None
    
def is_list_meaningfully_empty(my_list):
    return all(item.strip() == b'' for item in my_list)

def authenticate_visitor(DB_PATH, email: str) -> str | None:
    log.info(f"Authenticating visitor with email: {email}")
    
    if not is_valid_email(email):
        log.critical("Authentication aborted.")
        return None

    try:
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            log.info("Connected to database successfully.")
            
            cursor.execute("SELECT visitor_id FROM visitors WHERE email = ?", (email,))
            result = cursor.fetchone()
            
            if result:
                visitor_id = result[0]
                log.info("Authentication successful. Visitor ID: %s", visitor_id)
                return visitor_id
            else:
                log.warning("Authentication failed. Email not found.")
                return None
    
    except Exception as e:
        log.error(f"Error during authentication: {e}")
        return None
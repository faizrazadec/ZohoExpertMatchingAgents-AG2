import uuid
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
import sqlite3
import json
import os

from logger.custom_logger import setup_logger

logger = setup_logger()

def is_valid_email(email: str) -> bool:
    logger.info(f"Validating email: {email}")
    try:
        validate_email(email)
        logger.info(f"Email {email} is valid.")
        return True
    except EmailNotValidError:
        logger.error(f"Email {email} is not valid.")
        return False
    
def is_valid_phone_number(phone: str) -> bool:
    logger.info(f"Validating phone number: {phone}")
    try:
        parsed_number = phonenumbers.parse(phone, None)
        phonenumbers.is_valid_number(parsed_number)
        logger.info(f"Phone number {phone} is valid.")
        return True
    except NumberParseException:
        logger.error(f"Phone number {phone} is not valid.")
        return False

def generate_id(email: str, phone: str) -> str:
    logger.info(f"Generating ID for email: {email} and phone: {phone}")
    if is_valid_email(email) and is_valid_phone_number(phone):
        try:
            name = f"{email}-{phone}"
            id = str(uuid.uuid5(uuid.NAMESPACE_DNS, name))
            logger.info(f"Generated ID: {id}")
            return id
        except Exception as e:
            logger.error(f"Error generating ID: {e}")
            return None
    else:
        logger.error(f"Invalid email or phone number provided.")
        return None
    
def authentication_email(DB_PATH, email: str) -> int | None:
    logger.info(f"Authenticating user with email: {email}")
    
    if not is_valid_email(email):
        logger.critical("Authentication aborted.")
        return None

    try:
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            logger.info("Connected to database successfully.")
            
            cursor.execute("SELECT client_id FROM clients WHERE email = ?", (email,))
            result = cursor.fetchone()
            
            if result:
                client_id = result[0]
                logger.info("Authentication successful. Client ID: %s", client_id)
                return client_id
            else:
                logger.warning("Authentication failed. Email not found.")
                return None
    
    except Exception as e:
        logger.error(f"Error during authentication: {e}")
        return None

def generate_temp_id(input_value: str) -> str:
    logger.info(f"Generating ID for input value: {input_value}")
    
    if "@" in input_value:
        if not is_valid_email(input_value):
            logger.error(f"Invalid email provided.")
            return None
    else:
        if not is_valid_phone_number(input_value):
            logger.error(f"Invalid phone number provided.")
            return None
    
    try:
        id = str(uuid.uuid5(uuid.NAMESPACE_DNS, input_value))
        logger.info(f"Generated ID: {id}")
        return id
    except Exception as e:
        logger.error(f"Error generating ID: {e}")
        return None
    
def is_list_meaningfully_empty(my_list):
    return all(item.strip() == b'' for item in my_list)

flag = {"flag": False,
        "user_id": None}
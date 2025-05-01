import sqlite3
import uuid
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException

from logger.custom_logger import setup_logger

logger = setup_logger()

def is_valid_email(email: str) -> bool:
    try:
        validate_email(email)
        logger.info(f"Email {email} is valid.")
        return True
    except EmailNotValidError:
        logger.error(f"Email {email} is not valid.")
        return False
    
def is_valid_phone_number(phone: str) -> bool:
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

def insert_client(name, email, phone):

    client_id = generate_id(email, phone)
    print("++++", client_id)

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
    phone="+923327422241"
)

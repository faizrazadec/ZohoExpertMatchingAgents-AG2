import uuid
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException

from logger.custom_logger import setup_logger
from config.config import DB_PATH

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
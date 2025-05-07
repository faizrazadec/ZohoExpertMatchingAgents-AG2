import os
from dotenv import load_dotenv
from logger.custom_logger import setup_logger

logger = setup_logger()
load_dotenv()

try:
    logger.info("Loading environment variables from .env file.")
    EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
    EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
    IMAP_SERVER = os.getenv("IMAP_SERVER")
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    DB_PATH = os.getenv("DB_PATH")
    MODEL_NAME = os.getenv("MODEL_NAME")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    llm_config = {
        "config_list": [
            {
                "api_type": "openai",
                "model": MODEL_NAME,
                "api_key": OPENAI_API_KEY,
            }
        ],
    }

except:
    logger.error("Failed to load environment variables. Please check your .env file.")

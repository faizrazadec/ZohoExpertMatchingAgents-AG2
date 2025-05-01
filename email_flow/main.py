import imaplib
import time

from logger.custom_logger import setup_logger

from .utils import (
    is_list_meaningfully_empty,
)

from config.config import (
    EMAIL_ACCOUNT,
    EMAIL_APP_PASSWORD,
    IMAP_SERVER,
    SMTP_SERVER,
    DB_PATH,
    MODEL_NAME
)

from .prompts import (
    system_prompt_not_client,
    system_prompt_email_generator
)

from .flow import (
    process_incoming_emails
)

logger = setup_logger(__name__)

def email_trigger(IMAP_SERVER, EMAIL_ACCOUNT, EMAIL_APP_PASSWORD):
    logger.info("Looking for new emails...")
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, EMAIL_APP_PASSWORD)
        mail.select('inbox')

        _, response = mail.search(None, '(UNSEEN)')

        is_new = is_list_meaningfully_empty(response)
        if is_new:
            logger.info("No new emails.")
            mail.logout()
            return False
        
        else:
            logger.info("New emails.")
            mail.logout()
            return True
    except imaplib.IMAP4.error as e:
        logger.error("Failed to login to email account or fetch emails: %s", e)
        return False
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        return False

if __name__ == "__main__":
    logger.info("Starting Email Bot...")

    while True:
        try:
            if email_trigger(IMAP_SERVER, EMAIL_ACCOUNT, EMAIL_APP_PASSWORD):
                process_incoming_emails(DB_PATH, system_prompt_not_client, system_prompt_email_generator, EMAIL_ACCOUNT, SMTP_SERVER, IMAP_SERVER, EMAIL_APP_PASSWORD)
        except Exception as e:
            logger.error("Failed to process incoming emails: %s", e)
        time.sleep(30)
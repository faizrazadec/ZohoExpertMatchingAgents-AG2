import imaplib

from .utils import (
    is_list_meaningfully_empty,
)

from logger.custom_logger import setup_logger

log = setup_logger(__name__)

def trigger(IMAP_SERVER, EMAIL_ACCOUNT, EMAIL_APP_PASSWORD):
    log.info("Looking for new emails...")
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, EMAIL_APP_PASSWORD)
        mail.select('inbox')

        _, response = mail.search(None, '(UNSEEN)')

        is_new = is_list_meaningfully_empty(response)
        if is_new:
            log.info("No new emails.")
            mail.logout()
            return False
        
        else:
            log.info("New emails.")
            mail.logout()
            return True
    except imaplib.IMAP4.error as e:
        log.error("Failed to login to email account or fetch emails: %s", e)
        return False
    except Exception as e:
        log.error("Unexpected error: %s", e)
        return False
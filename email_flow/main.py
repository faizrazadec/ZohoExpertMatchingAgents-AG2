import time

from logger.custom_logger import setup_logger

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

from .email_trigger import (
    trigger,
)

log = setup_logger(__name__)

if __name__ == "__main__":
    log.info("Starting Email Bot...")

    while True:
        try:
            if trigger(IMAP_SERVER, EMAIL_ACCOUNT, EMAIL_APP_PASSWORD):
                process_incoming_emails(DB_PATH, system_prompt_not_client, system_prompt_email_generator, EMAIL_ACCOUNT, SMTP_SERVER, IMAP_SERVER, EMAIL_APP_PASSWORD)
        except Exception as e:
            log.error("Failed to process incoming emails: %s", e)
        time.sleep(30)
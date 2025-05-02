import os
from dotenv import load_dotenv

from .email_flow_functions import (
    fetch_unread_emails,
    send_email,
)

from .db_flow_functions import (
    save_message,
    get_conversation
)

from .utils import (
    authentication_email,
    generate_temp_id,
)

from .openai_flow_functions import (
    generate_visitor_reply,
    generate_client_reply
)

from logger.custom_logger import setup_logger

log = setup_logger(__name__)
load_dotenv()

def process_incoming_emails(DB_PATH, system_prompt_not_client, system_prompt_email_generator, EMAIL_ACCOUNT, SMTP_SERVER, IMAP_SERVER, EMAIL_APP_PASSWORD):
    log.info("Email flow triggered.")
    try:
        new_emails = fetch_unread_emails(IMAP_SERVER, EMAIL_ACCOUNT, EMAIL_APP_PASSWORD)
    except Exception as e:
        log.error("Failed to fetch unread emails: %s", e)
        return

    for email_data in new_emails:
        try:
            sender = email_data['from']
            body = email_data['body']
            subject = email_data['subject']
            message_id = email_data.get('message_id')
            # thread_id = subject
            client_id = authentication_email(DB_PATH, sender)

            if client_id:
                save_message(DB_PATH, is_client=True, sender=sender, message=body, user_id=client_id)
                conversation = get_conversation(DB_PATH, user_id=client_id)
                reply_body = generate_client_reply(conversation, system_prompt_email_generator)
                save_message(DB_PATH, is_client=True, sender=EMAIL_ACCOUNT, message=reply_body, user_id=client_id)
                success = send_email(sender, "Re: " + subject, reply_body, EMAIL_ACCOUNT, SMTP_SERVER, EMAIL_APP_PASSWORD, in_reply_to=message_id)
                if not success:
                    log.error(f"Failed to send email to {sender}")
                else:
                    log.info(f"Email successfully sent to {sender}")

            else:
                log.info("Sender not found in database. Sending onboarding invitation...")
                if os.environ.get("FLAG") == 'true':
                    user_id = generate_temp_id(sender)
                    log.critical("False User ID: %s", user_id)
                else:
                    user_id = os.environ.get("USER_ID")
                    log.critical("True User ID: %s", user_id)

                # temp_id = generate_temp_id(sender)
                save_message(DB_PATH, is_client=False, sender=sender, message=body, user_id=user_id)
                conversation = get_conversation(DB_PATH, user_id=user_id)
                reply_body = generate_visitor_reply(conversation, system_prompt_not_client, visitor_email=sender)
                save_message(DB_PATH, is_client=False, sender=EMAIL_ACCOUNT, message=reply_body, user_id=user_id)
                success = send_email(sender, "Re: " + subject, reply_body, EMAIL_ACCOUNT, SMTP_SERVER, EMAIL_APP_PASSWORD, in_reply_to=message_id)
                if not success:
                    log.error(f"Failed to send onboarding email to {sender}")
                else:
                    log.info(f"Onboarding email successfully sent to {sender}")
        except Exception as e:
            log.error("Failed to process email from %s: %s", sender, e)
import imaplib
import email
from email.mime.text import MIMEText
import smtplib

from logger.custom_logger import setup_logger

from .utils import is_list_meaningfully_empty

log = setup_logger(__name__)
    
def mail_login(IMAP_SERVER, EMAIL_ACCOUNT, EMAIL_APP_PASSWORD):
    log.info("Logging in to email account...")
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, EMAIL_APP_PASSWORD)
        log.info("Logged in to email account successfully.")
        return mail
    except imaplib.IMAP4.error as e:
        log.error("Failed to login to email account: %s. Please check your credentials or IMAP server settings.", e)
        return None
    
def fetch_unread_emails(IMAP_SERVER, EMAIL_ACCOUNT, EMAIL_APP_PASSWORD):
    log.info("Fetching unread emails...")
    try:
        mail = mail_login(IMAP_SERVER, EMAIL_ACCOUNT, EMAIL_APP_PASSWORD)
        if mail is None:
            log.error("Failed to login to email account.")
            return []

        mail.select('inbox')

        status, response = mail.search(None, '(UNSEEN)')

        if status != 'OK':
            log.error("Failed to search for unread emails: %s", status)
            return []

        is_new = is_list_meaningfully_empty(response)
        if is_new:
            log.info("No new emails.")
            return []
        else:
            log.info("New emails.")

        unread_msg_nums = response[0].split()

        emails = []
        for e_id in unread_msg_nums:
            try:
                _, data = mail.fetch(e_id, '(RFC822)')
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)

                from_email = email.utils.parseaddr(msg['From'])[1]
                subject = msg['Subject']

                if msg.is_multipart():
                    log.info("Email is multipart")
                    body = ''
                    for part in msg.walk():
                        if part.get_content_type() == 'text/plain':
                            body += part.get_payload(decode=True).decode()
                else:
                    body = msg.get_payload(decode=True).decode()

                emails.append({
                    "from": from_email,
                    "subject": subject,
                    "body": body,
                    "message_id": msg['Message-ID']
                })
            except Exception as e:
                log.error("Failed to parse email: %s", e)

        mail.logout()
        log.info("Logged out to email account successfully.")
        return emails
    except Exception as e:
        log.error("Failed to fetch unread emails: %s", e)
        return []
    
def send_email(to_address, subject, body, EMAIL_ACCOUNT, SMTP_SERVER, EMAIL_APP_PASSWORD, in_reply_to=None):
    log.info("Sending email to %s", to_address)
    if body is None:
        log.error("Email body is None. Cannot send email.")
        return False

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ACCOUNT
    msg['To'] = to_address

    if in_reply_to:
        msg['In-Reply-To'] = in_reply_to
        msg['References'] = in_reply_to

    try:
        log.info("Connecting to SMTP server...")
        with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server:
            # server.set_debuglevel(1)
            server.login(EMAIL_ACCOUNT, EMAIL_APP_PASSWORD)
            log.info("Sending email...")
            server.sendmail(EMAIL_ACCOUNT, to_address, msg.as_string())
            log.info("Email sent successfully.")
        return True
    except smtplib.SMTPException as e:
        log.error("Failed to send email via SMTP server: %s", e)
        return False
    except Exception as e:
        log.error("Unexpected error sending email: %s", e)
        return False
import sqlite3
import imaplib
import email
import smtplib
from email.mime.text import MIMEText
import time

from custom_logger import setup_logger

logger = setup_logger(__name__)

EMAIL_ACCOUNT = "t16624452@gmail.com"
EMAIL_APP_PASSWORD = "ziif apbl ypgf zpmi "
IMAP_SERVER = "imap.gmail.com"
SMTP_SERVER = "smtp.gmail.com"
DB_PATH = "db/zoho_database.db"

def mail_login(IMAP_SERVER, EMAIL_ACCOUNT, EMAIL_APP_PASSWORD):
    logger.info("Logging in to email account...")
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, EMAIL_APP_PASSWORD)
        logger.info("Logged in to email account successfully.")
        return mail
    except imaplib.IMAP4.error as e:
        logger.error("Failed to login to email account: %s", e)
        return None

mail_login(IMAP_SERVER, EMAIL_ACCOUNT, EMAIL_APP_PASSWORD)


def fetch_unread_emails():
    logger.info("Fetching unread emails...")
    mail = mail_login(IMAP_SERVER, EMAIL_ACCOUNT, EMAIL_APP_PASSWORD)
    mail.select('inbox')

    status, response = mail.search(None, '(UNSEEN)')

    if status != 'OK':
        logger.error("Status: %s", status)
    elif status == 'OK':
        logger.info("Status: %s", status)

    unread_msg_nums = response[0].split()

    emails = []
    for e_id in unread_msg_nums:
        _, data = mail.fetch(e_id, '(RFC822)')
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        from_email = email.utils.parseaddr(msg['From'])[1]
        subject = msg['Subject']
        
        if msg.is_multipart():
            logger.info("Email is multipart")
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
            "message_id": msg['Message-ID']  # <-- Important
        })

    mail.logout()
    logger.info("Logged out to email account successfully.")
    return emails

def authentication(email_address):
    logger.info("Authenticating email address: %s", email_address)
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        logger.info("Connected to database successfully.")

        try:
            logger.info("Checking if email exists in database...")
            cursor.execute("SELECT * FROM existing_clients WHERE email=?", (email_address,))
            result = cursor.fetchone()
            return result is not None
        finally:
            logger.info("Closing database connection...")
            connection.close()
    except sqlite3.Error as e:
        logger.error("Failed to connect to database: %s", e)
        return None

def send_email(to_address, subject, body, EMAIL_ACCOUNT, SMTP_SERVER, in_reply_to=None):
    logger.info("Sending email to %s", to_address)
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ACCOUNT
    msg['To'] = to_address

    if in_reply_to:
        msg['In-Reply-To'] = in_reply_to
        msg['References'] = in_reply_to

    try:
        logger.info("Connecting to SMTP server...")
        with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server:
            logger.info("Logging in to Email account...")
            server.login(EMAIL_ACCOUNT, EMAIL_APP_PASSWORD)
            logger.info("Sending email...")
            server.sendmail(EMAIL_ACCOUNT, to_address, msg.as_string())
    except smtplib.SMTPException as e:
        logger.error("Failed to send email: %s", e)
        return False

def process_incoming_emails():
    logger.info("Processing incoming emails...")
    new_emails = fetch_unread_emails()
    for email_data in new_emails:
        sender = email_data['from']
        body = email_data['body']
        subject = email_data['subject']
        message_id = email_data.get('message_id')

        if authentication(sender):
            if "connect" in body.lower():
                reply_body = "Thank you! We will connect you with an expert shortly."
            elif "explore" in body.lower():
                reply_body = "Feel free to explore our platform! Here's a link: https://yourplatform.example.com"
            else:
                reply_body = "Would you like to Explore our Platform or Connect with an Expert? Please reply with your preference."

            send_email(sender, "Re: " + subject, reply_body, EMAIL_ACCOUNT, SMTP_SERVER, in_reply_to=message_id)

        else:
            reply_body = "Thank you for reaching out! We couldn't find you in our database.\nWould you like to schedule a call to set up your account?"
            send_email(sender, "Re: " + subject, reply_body, EMAIL_ACCOUNT, SMTP_SERVER, in_reply_to=message_id)


if __name__ == "__main__":
    while True:
        logger.info("Checking for new emails...")
        process_incoming_emails()
        time.sleep(60)

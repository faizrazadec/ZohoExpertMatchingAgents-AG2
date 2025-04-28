import sqlite3
import imaplib
import email
import smtplib
from email.mime.text import MIMEText
import time
from openai import OpenAI
from dotenv import load_dotenv

from custom_logger import setup_logger
from prompts import (
    system_prompt_email_generator
)

load_dotenv()
logger = setup_logger(__name__)

EMAIL_ACCOUNT = "t16624452@gmail.com"
EMAIL_APP_PASSWORD = "ziif apbl ypgf zpmi "
IMAP_SERVER = "imap.gmail.com"
SMTP_SERVER = "smtp.gmail.com"
DB_PATH = "db/zoho_database.db"

def save_message(thread_id, sender, message, client_id, source="email"):
    logger.info("Saving message to database...")
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.execute('''
        INSERT INTO conversation_history (thread_id, sender, message, client_id, source)
        VALUES (?, ?, ?, ?, ?)
        ''', (thread_id, sender, message, client_id, source))
        connection.commit()
        connection.close()
        logger.info("Saved to database successfully.")
    except sqlite3.Error as e:
        logger.error("Failed to save to database: %s", e)
        return


def get_conversation(client_id):
    logger.info("Fetching conversation history from database...")
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute('''
        SELECT sender, message FROM conversation_history
        WHERE client_id = ?
        ORDER BY timestamp ASC
    ''', (client_id,))
    history = cursor.fetchall()
    connection.close()
    return history
    

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
    
def is_list_meaningfully_empty(my_list):
    return all(item.strip() == b'' for item in my_list)

def fetch_unread_emails():
    logger.info("Fetching unread emails...")
    mail = mail_login(IMAP_SERVER, EMAIL_ACCOUNT, EMAIL_APP_PASSWORD)
    mail.select('inbox')

    status, response = mail.search(None, '(UNSEEN)')

    if status != 'OK':
        logger.error("Status: %s", status)
    elif status == 'OK':
        logger.info("Status: %s", status)

    is_new = is_list_meaningfully_empty(response)
    if is_new:
        logger.info("No new emails.")
    
    else:
        logger.info("New emails.")

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
            "message_id": msg['Message-ID']
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
            cursor.execute("SELECT client_id FROM clients WHERE email=?", (email_address,))
            result = cursor.fetchone()
            if result:
                client_id = result[0]
                logger.info("Authentication successful. Client ID: %s", client_id)
                return client_id
            else:
                logger.warning("Authentication failed. Email not found.")
                return None
        finally:
            logger.info("Closing database connection...")
            connection.close()
    except sqlite3.Error as e:
        logger.error("Error: %s", e)
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
            # server.set_debuglevel(1)
            server.login(EMAIL_ACCOUNT, EMAIL_APP_PASSWORD)
            logger.info("Sending email...")
            server.sendmail(EMAIL_ACCOUNT, to_address, msg.as_string())
            server.quit()
            logger.info("Email sent successfully.")
        return True
    except smtplib.SMTPException as e:
        logger.error("Failed to connect to SMTP server: %s", e)
        return False
    
def generate_reply(client_email_body, system_prompt):
    logger.info("Generating reply using LLM...")

    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Client's Email:\n{client_email_body}\n\nWrite a reply."}
            ],
            temperature=0.5,
            max_tokens=300
        )

        reply_text = response.choices[0].message.content
        return reply_text

    except Exception as e:
        logger.error("Failed to generate reply: %s", e)
        return "Thank you for reaching out! We will get back to you shortly."

def process_incoming_emails(system_prompt_email_generator):
    logger.info("Processing incoming emails...")
    new_emails = fetch_unread_emails()
    
    for email_data in new_emails:
        sender = email_data['from']
        body = email_data['body']
        subject = email_data['subject']
        message_id = email_data.get('message_id')
        thread_id = subject
        client_id = authentication(sender)

        if client_id:
            save_message(thread_id=thread_id, sender=sender, message=body, client_id=client_id)
            conversation = get_conversation(client_id=client_id)
            reply_body = generate_reply(conversation, system_prompt_email_generator)
            save_message(thread_id=thread_id, sender=EMAIL_ACCOUNT, message=reply_body, client_id=client_id)
            success = send_email(sender, "Re: " + subject, reply_body, EMAIL_ACCOUNT, SMTP_SERVER, in_reply_to=message_id)
            if not success:
                logger.error(f"Failed to send email to {sender}")
            else:
                logger.info(f"Email successfully sent to {sender}")

        else:
            logger.info("Sender not found in database. Sending onboarding invitation...")
            reply_body = (
                "Thank you for reaching out! Seems like you're not a registered client.\n"
                "Would you like to schedule a call to set up your account?"
            )
            save_message(thread_id=thread_id, sender=EMAIL_ACCOUNT, message=reply_body, client_id=None)
            success = send_email(sender, "Re: " + subject, reply_body, EMAIL_ACCOUNT, SMTP_SERVER, in_reply_to=message_id)
            if not success:
                logger.error(f"Failed to send onboarding email to {sender}")
            else:
                logger.info(f"Onboarding email successfully sent to {sender}")


if __name__ == "__main__":
    logger.info("Starting Email Bot...")

    while True:
        process_incoming_emails(system_prompt_email_generator)
        time.sleep(60)

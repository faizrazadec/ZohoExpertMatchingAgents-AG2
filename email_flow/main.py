import sqlite3
import imaplib
import email
import smtplib
from email.mime.text import MIMEText
import time
from openai import OpenAI
import json
import os
from openai.types.chat import ChatCompletionMessageToolCall
from dotenv import load_dotenv

from custom_logger import setup_logger

from prompts import (
    system_prompt_email_generator
)

load_dotenv()

logger = setup_logger(__name__)

# Load environment variables
EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER")
SMTP_SERVER = os.getenv("SMTP_SERVER")
DB_PATH = os.getenv("DB_PATH")
print(EMAIL_ACCOUNT, EMAIL_APP_PASSWORD, IMAP_SERVER, SMTP_SERVER, DB_PATH)

# Tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "retrieve_experts",
            "description": "Retrieve expert data from the database",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]

def save_message(thread_id, sender, message, client_id, source="email"):
    """
    Saves a message to the conversation history in the SQLite database.
    Args:
        thread_id (str): The ID of the email thread.
        sender (str): The sender of the message.
        message (str): The content of the message.
        client_id (str): The ID of the client.
        source (str): The source of the message (default is "email").
    """
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
    """Get conversation history for a specific client from the database.
    Args:
        client_id (str): The ID of the client whose conversation history is to be fetched.
    Returns:
        list: A list of tuples containing the sender and message.
    """
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
    """Login to the email account using IMAP.
    Args:
        IMAP_SERVER (str): The IMAP server address.
        EMAIL_ACCOUNT (str): The email account username.
        EMAIL_APP_PASSWORD (str): The app password for the email account.
    Returns:
        imaplib.IMAP4_SSL: An authenticated IMAP connection object.
    """
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
    """Check if a list is meaningfully empty (i.e., all items are empty strings).
    Args:
        my_list (list): The list to check.
    Returns:
        bool: True if the list is meaningfully empty, False otherwise.
    """
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
    """
    Authenticate a client by checking if their email address exists in the database.
    Args:
        email_address (str): The email address of the client.
    Returns:
        str: The client ID if authentication is successful, None otherwise.
    """
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
    """
    Send an email using SMTP.
    Args:
        to_address (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The body of the email.
        EMAIL_ACCOUNT (str): The sender's email account.
        SMTP_SERVER (str): The SMTP server address.
        in_reply_to (str, optional): The message ID of the email being replied to.
    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
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

def retrieve_experts():
    """
    Retrieve a list of experts from the database.
    Returns:
        list: A list of dictionaries containing expert information.
    """
    logger.info("Retrieving experts from database...")
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM experts")
        column_names = [description[0] for description in cursor.description]
        experts = cursor.fetchall()
        return [dict(zip(column_names, row)) for row in experts]
    
    except Exception as e:
        logger.error("Failed to retrieve experts: %s", e)
        return {"status": "error", "message": str(e), "code": 500}
    
    finally:
        connection.close()
    
def generate_reply(conversation, system_prompt):
    """
    Generate a reply using the LLM with tool support.
    Args:
        conversation (list): The conversation history.
        system_prompt (str): The system prompt for the LLM.
    Returns:
        str: The generated reply.
    """
    logger.info("Generating reply using LLM with tool support...")

    try:
        client = OpenAI()

        messages = [
            {"role": "system", "content": system_prompt}
        ] + [{"role": "user", "content": m[1]} if m[0] != EMAIL_ACCOUNT else {"role": "assistant", "content": m[1]} for m in conversation]

        response = client.chat.completions.create(
            model="gpt-4.1-mini",  # or latest tool-supporting model
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.5,
            max_tokens=500
        )

        reply = response.choices[0].message

        if reply.tool_calls:
            tool_call: ChatCompletionMessageToolCall = reply.tool_calls[0]
            if tool_call.function.name == "retrieve_experts":
                logger.info("Tool call detected: retrieve_experts")
                tool_result = retrieve_experts()
                logger.info("Tool output: %s", tool_result)

                follow_up_response = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=messages + [
                        {"role": "assistant", "tool_call_id": tool_call.id, "content": None, "tool_calls": [tool_call]},
                        {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(tool_result)}
                    ],
                    temperature=0.5
                )

                return follow_up_response.choices[0].message.content

        return reply.content

    except Exception as e:
        logger.error("Failed to generate reply: %s", e)
        return "Thank you for reaching out! We will get back to you shortly."

def process_incoming_emails(system_prompt_email_generator):
    """
    Process incoming emails and generate replies.
    Args:
        system_prompt_email_generator (str): The system prompt for the email generator.
    Returns:
        None
    """
    logger.info("Email flow triggered.")
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

def email_trigger():
    """
    Check for new emails in the inbox.
    Returns:
        bool: True if new emails are found, False otherwise.
    """
    logger.info("Looking for new emails...")
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, EMAIL_APP_PASSWORD)
    except imaplib.IMAP4.error as e:
        logger.error("Failed to login to email account: %s", e)

    mail.select('inbox')

    status, response = mail.search(None, '(UNSEEN)')

    if status != 'OK':
        logger.error("Status: %s", status)
    elif status == 'OK':
        logger.info("Status: %s", status)

    is_new = is_list_meaningfully_empty(response)
    if is_new:
        logger.info("No new emails.")
        mail.logout()
        return False
    
    else:
        logger.info("New emails.")
        mail.logout()
        return True

if __name__ == "__main__":
    logger.info("Starting Email Bot...")

    while True:
        if email_trigger():
            process_incoming_emails(system_prompt_email_generator)
        time.sleep(60)

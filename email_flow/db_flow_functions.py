import sqlite3

from logger.custom_logger import setup_logger

logger = setup_logger()

def save_message(DB_PATH, is_client, sender, message, user_id, channel="email"):
    logger.info("Saving message to database...")
    try:
        with sqlite3.connect(DB_PATH) as connection:
            logger.info("Connected to database successfully.")
            cursor = connection.cursor()
            cursor.execute('''
            INSERT INTO chat_history (is_client, sender, message, user_id, channel)
            VALUES (?, ?, ?, ?, ?)
            ''', (is_client, sender, message, user_id, channel))
            connection.commit()
            logger.info("Saved to database successfully.")
    except sqlite3.Error as e:
        logger.error("Failed to save to database: %s", e)

def get_conversation(DB_PATH, user_id):
    logger.info("Fetching conversation history from database...")
    try:
        with sqlite3.connect(DB_PATH) as connection:
            logger.info("Connected to database successfully.")
            cursor = connection.cursor()
            cursor.execute('''
                SELECT sender, message FROM chat_history
                WHERE user_id = ?
                ORDER BY timestamp ASC
            ''', (user_id,))
            history = cursor.fetchall()
            logger.info("Conversation history fetched successfully.")
            return history
    except sqlite3.Error as e:
        logger.error("Failed to fetch conversation history: %s", e)
        return []
import sqlite3
import json

from config.config import (
    DB_PATH
)

from .utils import (
    is_valid_email,
    is_valid_phone_number,
    generate_id
)

from logger.custom_logger import setup_logger

log = setup_logger(__name__)

def authenticate_client(input_value: str) -> int | None:
    """Authenticate a client using their email or phone number.

    Attempts to validate and authenticate a client based on the provided input,
    which can be either an email address or a phone number. The function checks
    the input's validity, queries the database, and returns the associated
    client ID if authentication is successful.

    Args:
        input_value (str): The email address or phone number of the client.

    Returns:
        int | None: The client ID if authentication is successful; otherwise, None.

    Logs:
        - Info: Start of authentication, database connection status, and success.
        - Warning: If no client record is found.
        - Error: For invalid input or database exceptions.
    """
    log.info(f"Authenticating user: {input_value}")

    if "@" in input_value:
        if is_valid_email(input_value):
            try:
                with sqlite3.connect(DB_PATH) as connection:
                    cursor = connection.cursor()
                    log.info("connected to database successfully.")

                    cursor.execute("SELECT client_id FROM clients WHERE email = ?", (input_value,))
                    result = cursor.fetchone()
                    connection.commit()

                    if result:
                        client_id = result[0]
                        log.info("Authentication successful. Client ID: %s", client_id)
                        return {
                            "status": "success",
                            "message": "Client successfully authenticated on the plateform",
                            "client_id": client_id
                        }
                    else:
                        log.warning("Authentication failed. Email not found.")
                        return {
                            "status": "not_found",
                            "message": "Client's email not found. Proceed to authenticate_visitor"
                        }
            except Exception as e:
                log.error(f"Error during authentication: {e}")
                return {
                "status": "error",
                "message": f"Error during authentication: {e}"
                }
        else:
            log.error(f"Invalid email provided.")
            return {
                "status": "invalid_input",
                "message": "Invalid email provided"
            }
    else:
        if is_valid_phone_number(input_value):
            try:
                with sqlite3.connect(DB_PATH) as connection:
                    cursor = connection.cursor()
                    log.info("connected to database successfully.")

                    cursor.execute("SELECT client_id FROM clients WHERE phone = ?", (input_value,))
                    result = cursor.fetchone()
                    connection.commit()

                    if result:
                        client_id = result[0]
                        log.info("Authentication successful. Client ID: %s", client_id)
                        return {
                            "status": "success",
                            "message": "Client successfully authenticated on the plateform",
                            "client_id": client_id
                        }
                    else:
                        log.warning("Authentication failed. Phone not found.")
                        return {
                            "status": "not_found",
                            "message": "Client's phone not found. Proceed to authenticate_visitor"
                        }
            except Exception as e:
                log.error(f"Error during authentication: {e}")
                return {
                    "status": "error",
                    "message": f"Error during authentication: {e}"
                }
        else:
            log.error(f"Invalid phone number provided.")
            return {
                "status": "invalid_input",
                "message": "Invalid phone provided"
            }
        
def authenticate_visitor(input_value: str) -> int | None:
    """Authenticate a visitor using their email or phone number.

    Validates the given input as either an email address or a phone number.
    If valid, it attempts to locate a matching visitor record in the database
    and returns the corresponding visitor ID upon successful authentication.

    Args:
        input_value (str): The visitor's email address or phone number.

    Returns:
        int | None: The visitor ID if authentication is successful; otherwise, None.

    Logs:
        - Info: Input received, database connection, and authentication success.
        - Warning: If the email or phone number is not found in the database.
        - Error: If the input is invalid or a database error occurs.
    """
    log.info(f"Authenticating user: {input_value}")

    if "@" in input_value:
        if is_valid_email(input_value):
            try:
                with sqlite3.connect(DB_PATH) as connection:
                    cursor = connection.cursor()
                    log.info("connected to database successfully.")

                    cursor.execute("SELECT visitor_id FROM visitors WHERE email = ?", (input_value,))
                    result = cursor.fetchone()
                    connection.commit()

                    if result:
                        visitor_id = result[0]
                        log.info("Authentication successful. Visitor ID: %s", visitor_id)
                        return {
                            "status": "success",
                            "message": "Visitor successfully authenticated on the plateform",
                            "visitor_id": visitor_id
                        }
                    else:
                        log.warning("Authentication failed. Email not found.")
                        return {
                            "status": "not_found",
                            "message": "Visitor's email not found."
                        }
            except Exception as e:
                log.error(f"Error during authentication: {e}")
                return {
                    "status": "error",
                    "message": f"Error during authentication: {e}"
                }
        else:
            log.error(f"Invalid email provided.")
            return {
                "status": "invalid_input",
                "message": "Invalid email provided"
            }
    else:
        if is_valid_phone_number(input_value):
            try:
                with sqlite3.connect(DB_PATH) as connection:
                    cursor = connection.cursor()
                    log.info("connected to database successfully.")

                    cursor.execute("SELECT visitor_id FROM visitors WHERE phone = ?", (input_value,))
                    result = cursor.fetchone()
                    connection.commit()

                    if result:
                        visitor_id = result[0]
                        log.info("Authentication successful. Client ID: %s", visitor_id)
                        return {
                            "status": "success",
                            "message": "Visitor successfully authenticated on the plateform",
                            "visitor_id": visitor_id
                        }
                    else:
                        log.warning("Authentication failed. Phone not found.")
                        return {
                            "status": "not_found",
                            "message": "Visitor's phone not found."
                        }
            except Exception as e:
                log.error(f"Error during authentication: {e}")
                return {
                    "status": "error",
                    "message": f"Error during authentication: {e}"
                }
        else:
            log.error(f"Invalid phone number provided.")
            return {
                "status": "invalid_input",
                "message": "Invalid phone provided"
            }

def add_visitor(name: str, email: str, phone: str, consent: bool) -> int | None:
    """Add a new visitor to the database, ensuring unique email and phone.

    Validates the provided email and phone number, ensuring they are unique 
    in the system. If both are valid and not already associated with an existing 
    visitor, a unique visitor ID is generated and a new record is inserted into 
    the database.

    Args:
        name (str): The full name of the visitor.
        email (str): The visitor's email address.
        phone (str): The visitor's phone number.
        consent (bool): Whether the visitor has given consent.

    Returns:
        int | None: The generated visitor ID if insertion is successful; 
                    otherwise, None if the email or phone is already taken 
                    or an error occurs.

    Logs:
        - Info: Details of the visitor addition process and success.
        - Warning: If a visitor with the same email or phone number already exists.
        - Error: If the email, phone, or database operation fails.
    """

    log.info(f"Adding visitor: {name}")

    try:
        if not (is_valid_email(email) and is_valid_phone_number(phone)):
            log.error("Invalid email or phone number provided")
            return {
                "status": "invalid_input",
                "message": "Invalid email or phone number provided."
            }
        
        visitor_id = generate_id(email, phone)

        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            log.info("Connected to database successfully.")

            cursor.execute(
                "SELECT 1 FROM visitors WHERE email = ? OR phone = ?", (email, phone)
            )
            if cursor.fetchone():
                log.warning("Visitor with given email or phone already exists.")
                return {
                    "status": "duplicate",
                    "message": "A visitor with this email or phone number already exists."
                }

            cursor.execute("INSERT INTO visitors (visitor_id, name, email, phone, consent) VALUES (?, ?, ?, ?, ?)",
                        (visitor_id, name, email, phone, int(consent)))
            connection.commit()
            log.info("New visitor added. Visitor ID: %s", visitor_id)
            return {
                "status": "success",
                "message": "Visitor successfully added to the platform.",
                "visitor_id": visitor_id
            }
        
    except Exception as e:
        log.error("Error adding visitor: %s", e)
        return {
            "status": "error",
            "message": f"Error adding visitor: {e}"
        }
 
def hands_off(action: str) -> str:
    """
    Determines the next agent to hand off to based on the user's action or intent.

    Args:
        action (str): The action or intent provided by the user (e.g., 'connect', 'explore').

    Returns:
        str: The name of the agent to hand off control to.
    """

    action = action.lower()

    if action == "connect":
        return "connect_agent"
    elif action == "explore":
        return "explore_agent"
    else:
        return "the_human"

def retrive_experts():
    """
    Retrieves all expert records from the 'experts' table in the SQLite database.

    Returns:
        list: A list of dictionaries, each representing an expert record.
    """

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT * FROM experts")
        column_names = [description[0] for description in cursor.description]  # Get column names
        experts = cursor.fetchall()
        
        return [dict(zip(column_names, row)) for row in experts]
    
    except Exception as e:
        return json.dumps(
            {"status": "error",
             "message": str(e),
             "code": 500}
        )
    
    finally:
        connection.close()

import sqlite3
import json
from logger import setup_logger

logging = setup_logger()

db_path = '/home/faizraza/Projects/ZohoExpertMatchingAgents-AG2/db/zoho_expert_matching_agents.db'

def new_clients(name: str, email: str, phone: str, consent: bool):
    """
    Inserts a new client record into the 'new_clients' table of the SQLite database.

    Args:
        name (str): Full name of the client.
        email (str): Email address of the client.
        phone (str): Phone number of the client.
        consent (bool): Consent status of the client.

    Returns:
        str: A JSON-formatted string indicating the result of the operation.
             On success: {"status": "success", "message": "User added successfully", "code": 200}
             On error:   {"status": "error", "message": "<error message>", "code": 500}

    This function connects to the 'zoho_expert_matching_agents.db' database,
    attempts to insert a new record into the 'new_clients' table, and
    returns a JSON string representing the status of the operation.
    """

    connection = sqlite3.connect(db_path)
    logging.info("Connected to the database")

    cursor = connection.cursor()
    logging.info("Cursor created")
    try:
        cursor.execute("INSERT INTO new_clients (name, email, phone, consent) VALUES (?, ?, ?, ?)",
                        (name, email, phone, consent,))
        connection.commit()

        logging.info("Client added\nName: %s\nEmail: %s\nPhone: %s\nConsent: ", name, email, phone, consent)
        return json.dumps(
            {"status": "success", 
             "code": 200})
   
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return json.dumps(
            {"status": "error",
             "message": str(e),
             "code": 500}
            )
   
    finally:
        logging.critical("Closing the database connection")
        connection.close()

def authentication(email: str, phone: str):
    """
    Authenticate a client by checking if their email and phone number exist in the database.

    Parameters:
        email (str): The email address of the client.
        phone (str): The phone number of the client.

    Returns:
        str (JSON): A JSON-formatted response containing:
            - status (str): "success" if the client exists, "error" otherwise.
            - code (int): HTTP-style status code (200 for success, 404 if not found, 500 for error).
            - message (str, optional): Error message if an exception occurs.

    Behavior:
        - Connects to the SQLite database defined by `db_path`.
        - Executes a query to find a matching client record using both email and phone number.
        - If a match is found, logs the client info and returns a success response.
        - If no match is found, logs that the client does not exist and returns an error response.
        - If an exception occurs, logs the error and returns a 500 error response.
        - Closes the database connection in all cases.

    Logging:
        - Logs detailed info for client existence checks.
        - Logs critical message when closing the connection.
    """

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
 
    try:
        cursor.execute("SELECT * FROM new_clients WHERE email = ? AND phone = ?", (email, phone))
        user = cursor.fetchone()
        if user:
            logging.info("Client exist\nName: %s\nEmail: %s\nPhone: ", user[1], user[2], user[3])
            return json.dumps(
                {"status": "success",
                 "code": 200}
                )
        else:
            logging.error("Client desn't exist\nEmail: %s\nPhone: ", email, phone)
            return json.dumps(
                {"status": "error",
                "code": 404}
                )
        
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return json.dumps(
            {"status": "error",
             "message": str(e),
             "code": 500}
            )
    finally:
        logging.critical("Closing the database connection")
        connection.close()
       
 
# print(authentication(email="mzeeshan@gmail.com", phone="12567890"))


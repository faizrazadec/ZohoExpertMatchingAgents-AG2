import sqlite3
import json

db_path = '/home/faizraza/Projects/ZohoExpertMatchingAgents-AG2/db/zoho_database.db'

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

    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO new_clients (name, email, phone, consent) VALUES (?, ?, ?, ?)",
                        (name, email, phone, consent,))
        connection.commit()

        return json.dumps(
            {"status": "success", 
             "code": 200})
   
    except Exception as e:
        return json.dumps(
            {"status": "error",
             "message": str(e),
             "code": 500}
            )
   
    finally:
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
        cursor.execute("SELECT * FROM existing_clients WHERE email = ? AND phone = ?", (email, phone))
        user = cursor.fetchone()
        if user:
            return json.dumps(
                {"status": "success",
                 "code": 200}
                )
        else:
            return json.dumps(
                {"status": "error",
                "code": 404}
                )
        
    except Exception as e:
        return json.dumps(
            {"status": "error",
             "message": str(e),
             "code": 500}
            )
    finally:
        connection.close()
       
 
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

    connection = sqlite3.connect(db_path)
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

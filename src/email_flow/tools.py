add_visitor_tool = {
  "type": "function",
  "name": "add_visitor",
  "description": "Adds a new visitor to the database with the provided details",
  "strict": True,
  "parameters": {
    "type": "object",
    "required": [
      "name",
      "email",
      "phone",
      "consent"
    ],
    "properties": {
      "name": {
        "type": "string",
        "description": "The name of the visitor"
      },
      "email": {
        "type": "string",
        "description": "The email address of the visitor"
      },
      "phone": {
        "type": "string",
        "description": "The phone number of the visitor"
      },
      "consent": {
        "type": "boolean",
        "description": "Whether the visitor has given consent"
      }
    },
    "additionalProperties": False
  }
}

retrieve_expert_tool = {
  "type": "function",
  "name": "retrieve_experts",
  "description": "Retrieves a list of experts from the database",
  "strict": True,
  "parameters": {
    "type": "object",
    "properties": {},
    "additionalProperties": False
  }
}
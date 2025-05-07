from autogen import (
    register_function,
    GroupChat,
    GroupChatManager,
    Agent
)

from src.bot_flow.tools_functions import (
    authenticate_client,
    authenticate_visitor,
    add_visitor,
    hands_off,
    retrive_experts
)

from src.bot_flow.agents import (
    auth_agent,
    explore_agent,
    connect_agent,
    the_human,
    executor_agent,
    intent_agent,

)

from logger.custom_logger import setup_logger

log = setup_logger()

register_function(
    authenticate_visitor,
    caller=auth_agent,
    executor=executor_agent,
    description="Checks whether the user is a known visitor in the platform based on their email or phone number.",
)

register_function(
    authenticate_client,
    caller=auth_agent,
    executor=executor_agent,
    description="Verifies if the client is already registered in the platform using their email or phone number.",
)

register_function(
    add_visitor,
    caller=auth_agent,
    executor=executor_agent,
    description="Adds a new visitor to the platform by storing their name, email, phone number, and consent, or returns the existing visitor ID if they are already registered.",
)

register_function(
    hands_off    ,
    caller=intent_agent,
    executor=executor_agent,
    description="This function determines which specialized agent (e.g., explore_agent or connect_agent) should handle the next part of the conversation based on the client's intent. It returns the name of the agent to hand off to.",
)

register_function(
    retrive_experts    ,
    caller=connect_agent,
    executor=executor_agent,
    description="This function retrieves a list of all expert profiles stored in the database. It returns detailed information including name, email, qualifications, past companies, country, areas of expertise, years of experience, and timestamp. It is typically used by the connect_agent to find and display relevant experts to the client.",
)

def custom_speaker_selection_func(last_speaker: Agent, groupchat: GroupChat):
    """Custom function to determine the next speaker in a structured agent workflow."""
    messages = groupchat.messages

    log.critical(messages[-1])

    if last_speaker is the_human:
        return auth_agent
    
    elif last_speaker is auth_agent:
        if messages[-1].get("tool_calls"):
            return executor_agent
        else:
            return the_human 
        
    elif last_speaker is executor_agent:
        return auth_agent

    # if len(messages) <= 1:
    #     return the_human  # Start with the human agent

    # if len(messages) > 2  and last_speaker is the_human and  messages[-2].get("name") == "intent_agent":
    #     return intent_agent
    
    # elif len(messages) > 2  and last_speaker is the_human and messages[-2].get("name") == "connect_agent":
    #     return connect_agent

    # elif last_speaker is the_human:
    #     return auth_agent

    # elif last_speaker is auth_agent:
    #     if messages and messages[-1].get("tool_calls"):
    #         return executor_agent
    #     else:
    #         return the_human 
        
    # elif last_speaker is intent_agent:
    #     if messages and messages[-1].get("tool_calls"):
    #         return executor_agent
    #     else:
    #         return the_human
        
    # elif last_speaker is connect_agent:
    #     if messages and messages[-1].get("tool_calls"):
    #         return executor_agent
    #     else:
    #         return the_human

    # elif last_speaker is executor_agent:
    #     if messages[-1].get("role") == "tool" and messages[-1].get("content") == "{\"status\": \"success\", \"code\": 200}" and messages[-2]["tool_calls"][0]["function"]["name"] == "authentication":
    #         return intent_agent
        
    #     elif last_speaker is executor_agent and messages[-2].get("name") == "connect_agent":
    #         return the_human
        
    #     elif messages[-1].get("role") == "tool":
    #         tool_output = messages[-1].get("content")
    #         tool_name = messages[-2].get("tool_calls", [{}])[0].get("function", {}).get("name", "")

    #         if tool_name == "hands_off":
    #             if tool_output == "connect_agent":
    #                 return connect_agent
                
    #             elif tool_output == "explore_agent":
    #                 return explore_agent
                
    #     return the_human
        
    # else:
    #     return "random"
    
planning_chat = GroupChat(
    agents=[the_human, auth_agent, executor_agent, intent_agent, connect_agent, explore_agent],
    messages=[],
    max_round=100,
    speaker_selection_method=custom_speaker_selection_func,
)

planning_manager = GroupChatManager(
    groupchat=planning_chat,
)

design_chat_result = planning_manager.initiate_chat(
    recipient=the_human, message="Hello! To get started, could you please provide either your email address or your phone number? This will help me verify your registration status."
)

print("Design Chat Result:", design_chat_result.chat_history)

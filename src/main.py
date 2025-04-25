import os
from dotenv import load_dotenv

from autogen import (
    ConversableAgent,
    register_function,
    GroupChat,
    GroupChatManager,
    Agent
)

from functions import (
    new_clients,
    authentication,
    hands_off
)

from prompts import (
    system_prompt_auth_agent,
    system_prompt_intent_agent
)

load_dotenv()

llm_config = {
    "config_list": [
        {
            "api_type": "openai",
            "model": "gpt-4.1-mini",
            "api_key": os.getenv("OPENAI_API_KEY"),
        }
    ],
}

auth_agent = ConversableAgent(
    name="auth_agent",
    llm_config=llm_config,
    system_message=system_prompt_auth_agent,
    human_input_mode="NEVER",
    # functions=[new_clients, authentication, hands_off],
)

explore_agent = ConversableAgent(
    name="explore_agent",
    human_input_mode="NEVER",
    llm_config=llm_config,
    system_message="You are an Explore Agent. Your role is to assist clients in exploring the features and functionalities of our platform.",
)
connect_agent = ConversableAgent(
    name="connect_agent",
    human_input_mode="NEVER",
    llm_config=llm_config,
    system_message="You are an Connect Agent. Your role is to assist clients in connecting with experts or scheduling meetings.",
)

the_human = ConversableAgent(
    name="the_human",
    human_input_mode="ALWAYS"
)

executor_agent = ConversableAgent(
    name="executor_agent",
    human_input_mode="NEVER"
)

intent_agent = ConversableAgent(
    name="intent_agent",
    system_message=system_prompt_intent_agent,
    human_input_mode="NEVER",
    llm_config=llm_config
)

register_function(
    new_clients,
    caller=auth_agent,
    executor=executor_agent,
    description="This function will add a new client to the database.",
)

register_function(
    authentication    ,
    caller=auth_agent,
    executor=executor_agent,
    description="This function will authenticate a client by checking if their email and phone number exist in the database.",
)

register_function(
    hands_off    ,
    caller=intent_agent,
    executor=executor_agent,
    description="This function determines which specialized agent (e.g., explore_agent or connect_agent) should handle the next part of the conversation based on the client's intent. It returns the name of the agent to hand off to.",
)

def custom_speaker_selection_func(last_speaker: Agent, groupchat: GroupChat):
    """Custom function to determine the next speaker in a structured agent workflow."""
    messages = groupchat.messages

    # if len(messages) <= 1:
    #     return the_human  # Start with the human agent

    if len(messages) > 2  and last_speaker is the_human and  messages[-2].get("name") == "intent_agent":
        return intent_agent

    elif last_speaker is the_human:
        return auth_agent

    elif last_speaker is auth_agent:
        if messages and messages[-1].get("tool_calls"):
            return executor_agent
        else:
            return the_human 
        
    elif last_speaker is intent_agent:
        if messages and messages[-1].get("tool_calls"):
            return executor_agent
        else:
            return the_human

    elif last_speaker is executor_agent:
        if messages[-1].get("role") == "tool" and messages[-1].get("content") == "{\"status\": \"success\", \"code\": 200}" and messages[-2]["tool_calls"][0]["function"]["name"] == "authentication":
            return intent_agent
        
        elif messages[-1].get("role") == "tool":
            tool_output = messages[-1].get("content")
            tool_name = messages[-2].get("tool_calls", [{}])[0].get("function", {}).get("name", "")

            if tool_name == "hands_off":
                if tool_output == "connect_agent":
                    return connect_agent
                
                elif tool_output == "explore_agent":
                    return explore_agent
                
        return the_human
        
    else:
        return "random"
    
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
    recipient=the_human, message="How may I assist you today?"
)

print("Design Chat Result:", design_chat_result.chat_history)

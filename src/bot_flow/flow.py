import json

from autogen import (
    GroupChat,
    Agent
)

from src.bot_flow.agents import (
    auth_agent,
    the_human,
    executor_agent,
    intent_agent
)

from logger.custom_logger import setup_logger

log = setup_logger(__name__)

def custom_speaker_selection_func(last_speaker: Agent, groupchat: GroupChat):
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
        if messages[-1].get("role") == "tool" and messages[-2]["tool_calls"][0]["function"]["name"] == "authenticate_client":
            content = json.loads(messages[-1].get("content").replace("'", '"'))
            if content.get("status") == "success":
                return intent_agent
        
        # elif last_speaker is executor_agent and messages[-2].get("name") == "connect_agent":
        #     return the_human
        
        # elif messages[-1].get("role") == "tool":
        #     tool_output = messages[-1].get("content")
        #     tool_name = messages[-2].get("tool_calls", [{}])[0].get("function", {}).get("name", "")

        #     if tool_name == "hands_off":
        #         if tool_output == "connect_agent":
        #             return connect_agent
                
        #         elif tool_output == "explore_agent":
        #             return explore_agent

        else:
            return auth_agent   
        
    # elif last_speaker is executor_agent:
    #     return auth_agent

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
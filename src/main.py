import os
from dotenv import load_dotenv

from autogen import (
    ConversableAgent,
    register_function,
    initiate_swarm_chat,
    AfterWorkOption,
    GroupChat,
    GroupChatManager,
    Agent
)

from functions import (
    new_clients,
    authentication
)

from prompts import (
    system_prompt_auth_agent
)

load_dotenv()

llm_config = {
    "config_list": [
        {
            "api_type": "openai",
            "model": "gpt-4.1-nano",
            "api_key": os.getenv("OPENAI_API_KEY"),
        }
    ],
}

auth_agent = ConversableAgent(
    name="auth_agent",
    llm_config=llm_config,
    system_message=system_prompt_auth_agent,
    human_input_mode="NEVER",
    functions=[new_clients, authentication],
)

the_human = ConversableAgent(
    name="the_human",
    human_input_mode="ALWAYS"
)

executor_agent = ConversableAgent(
    name="executor_agent",
    human_input_mode="NEVER"
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

def custom_speaker_selection_func(last_speaker: Agent, groupchat: GroupChat):
    """Custom function to determine the next speaker in a structured agent workflow."""
    messages = groupchat.messages

    # if len(messages) <= 1:
    #     return the_human  # Start with the human agent

    if last_speaker is the_human:
        return auth_agent

    elif last_speaker is auth_agent:
        if messages and messages[-1].get("role") == "assistant" and messages[-1].get("tool_calls"):
            return executor_agent
        else:
            return the_human 

    elif last_speaker is executor_agent:
        return auth_agent

    else:
        return "random"
    
planning_chat = GroupChat(
    agents=[the_human, auth_agent, executor_agent],
    messages=[],
    speaker_selection_method=custom_speaker_selection_func,
)

planning_manager = GroupChatManager(
    groupchat=planning_chat,
)

design_chat_result = planning_manager.initiate_chat(
    recipient=the_human, message="How may I assist you today?"
)

# result, _, _ = initiate_swarm_chat(
#     initial_agent=the_human,
#     agents=[auth_agent, executor_agent, the_human],
#     messages="Hi, How may I assist you?",
#     swarm_manager_args={"llm_config": llm_config},
#     after_work=AfterWorkOption.SWARM_MANAGER
# )
print("Design Chat Result:", design_chat_result.chat_history)

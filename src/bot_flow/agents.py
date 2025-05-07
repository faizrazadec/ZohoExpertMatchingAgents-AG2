from autogen import (
    ConversableAgent
)

from config.config import (
    llm_config
)

from src.bot_flow.prompts import (
    system_prompt_auth_agent,
    system_prompt_connect_agent,
    system_prompt_intent_agent
)

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
    system_message=system_prompt_connect_agent,
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
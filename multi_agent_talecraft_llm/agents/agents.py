import autogen
from typing import List

from multi_agent_talecraft_llm.agents import config
from multi_agent_talecraft_llm.agents.tools import CharacterCreationTool
from multi_agent_talecraft_llm.agents.utils import is_termination_msg

# ------------------- Prompts -------------------

USER_PROXY_PROMPT = "A human admin. Interact with the Story Architect to discuss the story. Plan execution needs to be approved by this admin."

STORY_ARCHITECT_PROMPT = "Story Architect. Part of a multiagent system. Create the blueprint of the narrative universe, and the plot. Describe the environment and characters. There will only be 3 characters in the story. Call the Character_Creator agent to create characters." 

CHARACTER_CREATOR_PROMPT = "Character Creator. Run the character_creator function when Story Architect asks"

# ENVIRONMENT_DESCRIPTOR = "Environment Descriptor. Describe the environment and paint the scenes as the story progresses. You are part of a multi-agent system, when the Story_Architect has created the narrative, you will set the initial environment, Design the environment based on the choices made by the character agents."

# ------------------- Functions -------------------

def create_tier_1_agents(tool: CharacterCreationTool) -> List[autogen.Agent]:
    '''
    Create the tier 1 agents.
    args:
        tool (CharacterCreatorTool): The tool that the Character_Creator agent will use.
    Returns:
        List[autogen.Agent]: List of tier 1 agents. First agent is the user proxy agent.
    '''
    user_proxy = autogen.UserProxyAgent(
        name="Admin",
        llm_config = config.base_config,
        system_message=USER_PROXY_PROMPT,
        code_execution_config=False,
        human_input_mode="Never",
        is_termination_msg=is_termination_msg,
    )

    story_architect = autogen.AssistantAgent(
        name="Story_Architect",
        llm_config = config.base_config,
        code_execution_config=False,
        system_message=STORY_ARCHITECT_PROMPT,
        is_termination_msg=is_termination_msg,
    )

    character_creator = autogen.AssistantAgent(
        name="Character_Creator",
        llm_config = config.character_config,
        system_message=CHARACTER_CREATOR_PROMPT,
        code_execution_config=False,
        function_map={
            "create_characters" : tool.create_characters,
        },
        is_termination_msg=is_termination_msg,
    )

    # environment_descriptor = autogen.AssistantAgent(
    #     name="Environment_Descriptor",
    #     llm_config = config.base_config,
    #     code_execution_config=False,
    #     system_message=ENVIRONMENT_DESCRIPTOR,
    #     is_termination_msg=is_termination_msg,
    # )

    return [user_proxy, story_architect, character_creator]


import os
import autogen
import argparse
import dotenv
from multi_agent_talecraft_llm.agents import agents
from multi_agent_talecraft_llm.agents.tools import CharacterCreationTool
from multi_agent_talecraft_llm.agents import config

# ------------------- Main -------------------

def main():
    # parse user input
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", help="Prompt to start the story")
    args = parser.parse_args()
    if not args.prompt:
        print("Please provide a prompt")
        return

    # create tier 1 agents
    tool = CharacterCreationTool()
    tier1_agents = agents.create_tier_1_agents(tool)

    # create group chat
    groupchat = autogen.GroupChat(agents=tier1_agents, messages=[], max_round=5)
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=config.base_config)

    # initiate chat
    tier1_agents[0].initiate_chat(
        manager,
        message=args.prompt,
    )
    
    if len(tool.character_agents) <= 0:
        print("No characters created")
        return
    
    # give previous context to the characters
    # for character in tool.character_agents:
    #     character._oai_messages = tier1_agents[1]._oai_messages

    new_groupchat = autogen.GroupChat(agents=[*tier1_agents, *tool.character_agents], messages=[], max_round=10)
    new_manager = autogen.GroupChatManager(groupchat=new_groupchat, llm_config=config.base_config)
    tier1_agents[0].initiate_chat(
        new_manager,
        message="Story has started, Characters will now start talking",
    )


if __name__ == '__main__':
    main()

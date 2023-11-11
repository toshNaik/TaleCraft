import os
import autogen
import argparse
import dotenv

dotenv.load_dotenv()

assert os.environ.get("OPENAI_API_KEY"), "Please set OPENAI_API_KEY in .env file"

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", help="Prompt to start the story")
    args = parser.parse_args()
    if not args.prompt:
        print("Please provide a prompt")
        return

    # build the gpt configuration object
    # config_list_gpt4 = autogen.config_list_from_json(
    #     "OAI_CONFIG_LIST",
    #     filter_dict={
    #         "model": ["gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-v0314"],
    #     },
    # )

    gpt4_config = {
        "use_cache": False,
        "temperature": 0,
        "config_list": autogen.config_list_from_models(['gpt-3.5-turbo-1106']),
        "timeout": 120,
    }


    def is_termination_msg(content):
        have_content = content.get('content', None) is not None
        if have_content and 'END' in content['content']:
            return True
        return False

    def create_character(name, personality_prompt):
        character = autogen.AssistantAgent(
                name=name,
                llm_config=gpt4_config,
                system_message=f'Character you need to interact with other characters, follow the narrative and the environment. You are a character in a story with PERSONALITY. \n\n PERSONALITY\n {personality_prompt}',
                code_execution_config=False,
                is_termination_msg=is_termination_msg,
        )
        return character
 
    function_map = {
            "create_character" : create_character,
    }
    # create a set of agents with specific roles
    # admin user proxy agent - takes in prompt and manages the group chat
    user_proxy = autogen.UserProxyAgent(
        name="Admin",
        system_message='A human admin. Interact with the Story Architect to discuss the story. Plan execution needs to be approved by this admin.',
        code_execution_config=False,
        human_input_mode="Never",
        is_termination_msg=is_termination_msg,
    )

    story_architect = autogen.AssistantAgent(
        name="Story_Architect",
        llm_config=gpt4_config,
        code_execution_config=False,
        system_message='Story Architect. You hold the blueprint of the narrative universe, knowing the overarching plot and setting. You are part of a multi-agent system, interact with the Character_Creator agent to create characters. There can only be a maximum of 3 characters in the story. Ensure the story maintains continuity and steer the Character_Agents to align with the main narrative. Respond with END when the story concludes',
        is_termination_msg=is_termination_msg,
    )


    character_config = {
            **gpt4_config,
            "functions": [
                {
                    "name": "create_character",
                    "description": "Create character agents",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the character",
                            },
                            "personality_prompt": {
                                "type": "string",
                                "description": "Personality of the character",
                            },
                        },
                        "required": ["name", "personality_prompt"],
                    }
                }
            ],
    }
    character_creator = autogen.AssistantAgent(
        name="Character_Creator",
        llm_config=character_config,
        system_message='Character Creator. You can create a maximum of 3 characters in the story. You are part of a multi-agent system, when the Story_Architect and Environment_Descriptor call on you, create characters as per their definition. Create characters based on the narrative and the environment.',
        code_execution_config=False,
        function_map=function_map,
        is_termination_msg=is_termination_msg,
    )

    environment_descriptor = autogen.AssistantAgent(
        name="Envrionment_Descriptor",
        llm_config=gpt4_config,
        code_execution_config=False,
        system_message='Environment Descriptor. Describe the environment and paint the scenes as the story progresses. You are part of a multi-agent system, when the Story_Architect has created the narrative, you will set the initial environment, Design the environment based on the choices made by the character agents.',
        is_termination_msg=is_termination_msg,
    )

    

    groupchat = autogen.GroupChat(agents=[user_proxy, story_architect, environment_descriptor, character_creator], messages=[], max_round=5)
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=gpt4_config)

    user_proxy.initiate_chat(
        manager,
        message=args.prompt,
    )

    
if __name__ == '__main__':
    main()

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

    characters = []
    def create_characters(names, personality_prompts):
        for name, personality_prompt in zip(names, personality_prompts):
            characters.append(autogen.AssistantAgent(
                    name=name,
                    llm_config=gpt4_config,
                    system_message=f'You are a character agent, characters need to interact with other characters, while following the narrative set by Story_Architect and the environment set by Environment_Descriptor. You are a character in a story with NAME_AND_PERSONALITY. \n\n NAME_AND_PERSONALITY\n {personality_prompt}',
                    code_execution_config=False,
                    is_termination_msg=is_termination_msg,
            ))
        

    function_map = {
            "create_characters" : create_characters,
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
        system_message='Story Architect. You hold the blueprint of the narrative universe, knowing the overarching plot and setting. You are part of a multi-agent system, interact with the Character_Creator agent to create characters. There can only be a maximum of 3 characters in the story. Ensure the story maintains continuity according to the character dialogues. Keep the story very short. Respond with END when the story concludes.',
        is_termination_msg=is_termination_msg,
    )


    character_config = {
            **gpt4_config,
            "functions": [
                {
                    "name": "create_characters",
                    "description": "Create character agents",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "names": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                },
                                "maxItems": 3,
                                "description": "Names of the characters",
                            },
                            "personality_prompts": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                },
                                "maxItems": 3,
                                "description": "Personalities of the characters",
                            },
                        },
                        "required": ["names", "personality_prompts"],
                    }
                }
            ],
    }
    character_creator = autogen.AssistantAgent(
        name="Character_Creator",
        llm_config=character_config,
        system_message='Character Creator. You can create a maximum of 3 characters in the story. You are part of a multi-agent system, when the Story_Architect calls on you, create characters as per their definitions. Create characters based on the narrative and the environment.',
        code_execution_config=False,
        function_map=function_map,
        is_termination_msg=is_termination_msg,
    )

    environment_descriptor = autogen.AssistantAgent(
        name="Environment_Descriptor",
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
    
    if len(characters) <= 0:
        print("No characters created")
        return

    new_groupchat = autogen.GroupChat(agents=[user_proxy, story_architect, environment_descriptor, *characters], messages=groupchat.messages, max_round=10)
    new_manager = autogen.GroupChatManager(groupchat=new_groupchat, llm_config=gpt4_config)
    user_proxy.initiate_chat(
        new_manager,
        message='Story has started, character agents start talking',
    )


if __name__ == '__main__':
    main()

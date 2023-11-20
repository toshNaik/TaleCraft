import autogen
import dotenv
import os

# load .env file here because autogen.config_list_from_models() needs OPENAI_API_KEY
dotenv.load_dotenv()
assert os.environ.get("OPENAI_API_KEY"), "Please set OPENAI_API_KEY in .env file"

base_config = {
    "use_cache": False,
    "temperature": 0,
    "config_list": autogen.config_list_from_models(model_list=["gpt-4"]),
    "request_timeout": 120,
}

character_config = {
        **base_config,
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

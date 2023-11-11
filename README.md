## Story driven by multiple LLM agents
- User_Proxy agent - mimics the user
- Story_Architect agent - creates the narrative
- Environment_Descriptor agent - sets the environment for the story
- Character_Creator agent - creates characters on story architect's request

### TODO
- Newly created characters need context, they go off on a different tangent. (Agents have a _oai_message attribute which might be responsible for context, this can be cloned from existing agents and passed to newly created characters)
- Story_Architect - better prompt to ensure better character creation
- Character_Creator - better prompt to ensure better prompts for character personalities
- REFACTOR...

![Screenshot 1](imgs/ss1.png)
![Screenshot 2](imgs/ss2.png)


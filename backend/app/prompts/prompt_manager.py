from app.prompts.programming import PROGRAMMING_PROMPT
from app.prompts.gaming import GAMING_PROMPT
from app.prompts.startup import STARTUP_PROMPT
from app.prompts.cybersecurity import CYBERSECURITY_PROMPT
from app.prompts.content_creator import CONTENT_CREATOR_PROMPT


class PromptManager:

    PROMPTS = {
        "programming": PROGRAMMING_PROMPT,
        "gaming": GAMING_PROMPT,
        "startup": STARTUP_PROMPT,
        "cybersecurity": CYBERSECURITY_PROMPT,
        "content_creator": CONTENT_CREATOR_PROMPT
    }

    @classmethod
    def get_prompt(cls, domain: str):

        return cls.PROMPTS.get(
            domain,
            "You are a helpful AI assistant."
        )
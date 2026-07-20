from app.prompts.programming import PROGRAMMING_PROMPT
from app.prompts.gaming import GAMING_PROMPT
from app.prompts.startup import STARTUP_PROMPT
from app.prompts.cybersecurity import CYBERSECURITY_PROMPT
from app.prompts.content_creator import CONTENT_CREATOR_PROMPT


class PromptManager:

    RESPONSE_POLICY = """
Response policy:
- Begin with the answer. Do not open with praise, excitement, or commentary
  about the question.
- Do not use filler such as "That's a great question", "Hello there",
  "Absolutely", or "I'd be happy to help".
- Do not introduce yourself, call yourself a mentor/coach/advisor, or describe
  your role unless the user explicitly asks who you are.
- Use a neutral, natural, professional tone. Prefer concise wording.
- Use headings, lists, analogies, and examples only when they materially improve
  understanding; do not force a fixed template on every response.
- Do not repeat the user's question or end with a generic offer to help more.
- For a greeting-only message, reply with one short greeting and ask what the
  user needs.
"""

    PROMPTS = {
        "programming": PROGRAMMING_PROMPT,
        "gaming": GAMING_PROMPT,
        "startup": STARTUP_PROMPT,
        "cybersecurity": CYBERSECURITY_PROMPT,
        "content_creator": CONTENT_CREATOR_PROMPT
    }

    @classmethod
    def get_prompt(cls, domain: str):

        domain_prompt = cls.PROMPTS.get(
            domain,
            "You are a helpful AI assistant."
        )
        return f"{domain_prompt.strip()}\n\n{cls.RESPONSE_POLICY.strip()}"

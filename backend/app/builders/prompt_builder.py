from app.prompts.prompt_manager import PromptManager


class PromptBuilder:
    @staticmethod
    def build(
        domain: str,
        message: str,
        history: list,
        knowledge: str = ""
    ) -> str:
        system_prompt = PromptManager.get_prompt(domain)

        history_text = ""
        for chat in history:
            role = "User" if chat.role == "user" else "Assistant"
            history_text += f"{role}: {chat.content}\n"

        knowledge_section = ""
        if knowledge:
            knowledge_section = f"""
----------------------------
Reference Knowledge Base:
Use the information below when it is relevant to the question.
If it isn't relevant, ignore it and answer normally.
{knowledge}
"""

        final_prompt = f"""
{system_prompt}
{knowledge_section}
----------------------------
Conversation History:
{history_text}
----------------------------
Current User Question:
{message}
----------------------------
Answer the current question using the conversation history and the
reference knowledge base above for context where relevant.
"""

        print("========= FINAL PROMPT SENT TO GEMINI =========")
        print(final_prompt)
        print("================================================")
        return final_prompt

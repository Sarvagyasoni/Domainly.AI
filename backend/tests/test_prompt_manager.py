import unittest

from app.prompts.prompt_manager import PromptManager


class PromptManagerTests(unittest.TestCase):
    def test_all_domain_prompts_include_direct_response_policy(self):
        for domain in PromptManager.PROMPTS:
            with self.subTest(domain=domain):
                prompt = PromptManager.get_prompt(domain)
                self.assertIn("Begin with the answer", prompt)
                self.assertIn("Do not introduce yourself", prompt)
                self.assertIn("Do not open with praise", prompt)


if __name__ == "__main__":
    unittest.main()

import os
from dotenv import load_dotenv
from openai import OpenAI
from .prompt import Prompt


class LLM:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY")
            if load_dotenv(dotenv_path=".env")
            else None,
            base_url=os.getenv("DEEPSEEK_API_BASE_URL")
            if load_dotenv(dotenv_path=".env")
            else None,
        )

    def generate(self, prompt: Prompt) -> str:
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": prompt.get_system_msg()},
                {"role": "user", "content": prompt.get_user_msg()},
            ],
            response_format={"type": "json_object"},
        )
        output = response.choices[0].message.content or "{}"
        return output

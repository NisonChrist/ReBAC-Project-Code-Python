import os
from dotenv import load_dotenv
from openai import OpenAI
from .prompt import Prompt


class LLM:
    def __init__(self, prompt_list: list[Prompt]):
        self.model = "Deepseek-V3.2"
        self._api_key = (
            os.getenv("DEEPSEEK_API_KEY") if load_dotenv(dotenv_path=".env") else None
        )
        self.prompt_list = prompt_list
        self.history: list[dict[str, str | dict]] = []

    def generate(self) -> list[dict[str, str | dict]]:
        client = OpenAI(
            api_key=self._api_key,
            base_url="https://api.deepseek.com",
        )
        for prompt in self.prompt_list:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": prompt.get_system_msg()},
                    {"role": "user", "content": prompt.get_user_msg()},
                ],
                response_format={"type": "json_object"},
            )
            output = response.choices[0].message.content or "{}"
            self.history.append({"prompt": prompt.get_prompt(), "output": output})
        return self.history

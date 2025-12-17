import os
from dotenv import load_dotenv
from openai import OpenAI


class LLM:
    def __init__(self, model):
        self.model = "Deepseek-V3.2"
        self._api_key = (
            os.getenv("DEEPSEEK_API_KEY") if load_dotenv(dotenv_path="./.env") else None
        )

        self._last_chat = {"prompt": {"system": "", "user": ""}, "result": ""}

    def _store_chat(self, prompt: dict, result: str):
        self._last_chat["prompt"] = prompt
        self._last_chat["result"] = result
        return self._last_chat

    def _clean_last_chat(self):
        self._last_chat = {"prompt": {"system": "", "user": ""}, "result": ""}

    def input(self, prompt: dict[str, str]):
        self._last_chat["prompt"] = prompt
        return prompt

    def output(self) -> str:
        # ...
        client = OpenAI(
            api_key=self._api_key,
            base_url="https://api.deepseek.com",
        )

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": self._last_chat["prompt"]["system"]},
                {"role": "user", "content": self._last_chat["prompt"]["user"]},
            ],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content or "{}"
        self._clean_last_chat()
        return content

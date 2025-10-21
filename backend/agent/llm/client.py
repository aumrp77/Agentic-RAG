from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from dotenv import load_dotenv
from backend.agent.llm.settings import settings
import os

load_dotenv()

client = OpenAI(api_key=settings.api_key)


class LLMClient:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_response(self, messages: list[ChatCompletionMessageParam]) -> str | None:
        response = self.client.chat.completions.create(
            model=settings.model,
            messages=messages,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens
        )

        return response.choices[0].message.content
    
    def get_response_stream(self, messages: list[ChatCompletionMessageParam]):
        response = self.client.chat.completions.create(
            model=settings.model,
            messages=messages,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            stream=True
        )
        return response
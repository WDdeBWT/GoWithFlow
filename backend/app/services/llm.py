import httpx
from openai import OpenAI
from app.config import DEEPSEEK_API_KEY, DEEPSEEK_MODEL

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
    http_client=httpx.Client(trust_env=False),
)


def chat(messages: list, temperature: float = 0.2, response_format: dict | None = None) -> str:
    kwargs = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "temperature": temperature,
    }
    if response_format:
        kwargs["response_format"] = response_format
    resp = client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content

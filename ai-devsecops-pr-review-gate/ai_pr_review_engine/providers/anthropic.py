from typing import Any, Dict
import requests

from .base import AIProvider


class AnthropicProvider(AIProvider):
    def __init__(self, api_key: str, model: str) -> None:
        if not api_key:
            raise ValueError("api_key is required for anthropic provider")
        if not model:
            raise ValueError("model is required for anthropic provider")
        self.api_key = api_key
        self.model = model

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "max_tokens": 4096,
            "temperature": 0,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
            timeout=180,
        )
        response.raise_for_status()
        data = response.json()
        parts = data.get("content", [])
        return "\n".join(part.get("text", "") for part in parts if part.get("type") == "text")

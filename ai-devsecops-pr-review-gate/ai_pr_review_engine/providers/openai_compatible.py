from typing import Any, Dict
import requests

from .base import AIProvider


class OpenAICompatibleProvider(AIProvider):
    def __init__(self, api_key: str, model: str, base_url: str) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        if not model:
            raise ValueError("model is required")
        if not base_url:
            raise ValueError("base_url is required")

        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        url = f"{self.base_url}/chat/completions"
        payload: Dict[str, Any] = {
            "model": self.model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        # Some OpenAI-compatible endpoints support JSON mode, others do not.
        # If an endpoint rejects this, remove strict_json in provider-specific future config.
        payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        response = requests.post(url, headers=headers, json=payload, timeout=180)
        if response.status_code >= 400 and "response_format" in response.text:
            payload.pop("response_format", None)
            response = requests.post(url, headers=headers, json=payload, timeout=180)

        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

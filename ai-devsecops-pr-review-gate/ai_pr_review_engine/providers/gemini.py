from typing import Any, Dict
import requests

from .base import AIProvider


class GeminiProvider(AIProvider):
    def __init__(self, api_key: str, model: str) -> None:
        if not api_key:
            raise ValueError("api_key is required for gemini provider")
        if not model:
            raise ValueError("model is required for gemini provider")
        self.api_key = api_key
        self.model = model

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )

        payload: Dict[str, Any] = {
            "generationConfig": {
                "temperature": 0,
                "responseMimeType": "application/json",
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}],
                }
            ],
        }

        response = requests.post(url, json=payload, timeout=180)
        response.raise_for_status()
        data = response.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return '{"summary":"Gemini returned no candidates","findings":[]}'
        parts = candidates[0].get("content", {}).get("parts", [])
        return "\n".join(part.get("text", "") for part in parts)

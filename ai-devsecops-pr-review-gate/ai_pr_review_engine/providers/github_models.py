import os

from .openai_compatible import OpenAICompatibleProvider


class GitHubModelsProvider(OpenAICompatibleProvider):
    def __init__(self, model: str) -> None:
        token = os.getenv("GITHUB_TOKEN", "")
        super().__init__(
            api_key=token,
            model=model,
            base_url="https://models.github.ai/inference",
        )

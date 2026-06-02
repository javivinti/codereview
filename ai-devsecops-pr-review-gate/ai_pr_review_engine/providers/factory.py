from typing import Dict

from ai_pr_review_engine.providers.anthropic import AnthropicProvider
from ai_pr_review_engine.providers.base import AIProvider
from ai_pr_review_engine.providers.gemini import GeminiProvider
from ai_pr_review_engine.providers.github_models import GitHubModelsProvider
from ai_pr_review_engine.providers.mock import MockProvider
from ai_pr_review_engine.providers.openai_compatible import OpenAICompatibleProvider


def create_provider(
    provider: str,
    model: str,
    api_key: str,
    base_url: str,
) -> AIProvider:
    normalized = provider.strip().lower()

    if normalized == "mock":
        return MockProvider()

    if normalized == "github-models":
        return GitHubModelsProvider(model=model)

    if normalized == "openai-compatible":
        return OpenAICompatibleProvider(api_key=api_key, model=model, base_url=base_url)

    if normalized == "anthropic":
        return AnthropicProvider(api_key=api_key, model=model)

    if normalized == "gemini":
        return GeminiProvider(api_key=api_key, model=model)

    raise ValueError(
        f"Unsupported provider '{provider}'. "
        "Use github-models, openai-compatible, anthropic, gemini or mock."
    )

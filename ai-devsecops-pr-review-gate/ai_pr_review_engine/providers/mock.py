from .base import AIProvider


class MockProvider(AIProvider):
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        return """
{
  "summary": "Mock review completed. No real AI provider was called.",
  "impact_score": 1,
  "quality_score": "A",
  "findings": [],
  "positive_points": ["The review pipeline executed successfully."],
  "critical_violations": []
}
"""

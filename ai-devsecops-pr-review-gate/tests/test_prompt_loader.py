from ai_pr_review_engine.prompt_loader import parse_front_matter


def test_parse_front_matter():
    metadata, body = parse_front_matter("""---
provider: github-models
model: openai/gpt-4o
---
Hello
""")
    assert metadata["provider"] == "github-models"
    assert metadata["model"] == "openai/gpt-4o"
    assert body == "Hello"

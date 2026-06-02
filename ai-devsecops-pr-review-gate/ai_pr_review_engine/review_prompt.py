from typing import Optional


SYSTEM_PROMPT = """You are a senior DevSecOps reviewer.
You review Pull Requests using only the provided PR context.
You must not invent files, lines, endpoints, vulnerabilities, business rules, or dependencies.
Focus on issues introduced or worsened by the Pull Request.
Prefer high-confidence, actionable findings over generic advice.
Return strict JSON only.
"""


def build_final_prompt(
    prompt_body: str,
    pr_context: str,
    custom_instructions: str = "",
) -> str:
    extra = ""
    if custom_instructions:
        extra = f"\n## Runtime Custom Instructions\n\n{custom_instructions}\n"

    return f"""
{prompt_body}

{extra}

## Controlled Input

You must use only the following generated file as your source of truth.

<pr_context.md>
{pr_context}
</pr_context.md>

Return only valid JSON. Do not include markdown fences.
"""

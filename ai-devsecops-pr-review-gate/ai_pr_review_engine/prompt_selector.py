from typing import Any, Dict, List


DEFAULT_PROMPTS = {
    "backend-nestjs": "prompts/pullrequest/backend/nestjs/prompt.md",
    "backend-go": "prompts/pullrequest/backend/go/prompt.md",
    "terraform": "prompts/pullrequest/infrastructure/terraform/prompt.md",
    "generic-security": "prompts/pullrequest/generic/security/prompt.md",
}


def infer_stack(files: List[Dict[str, Any]]) -> str:
    names = [f.get("filename", "").lower() for f in files]

    if any(name.endswith(".tf") or "terraform/" in name for name in names):
        return "terraform"

    if any(name.endswith(".go") for name in names):
        return "backend-go"

    if any(
        name.endswith(".ts")
        or "nestjs" in name
        or "nest-cli.json" in name
        or "package.json" in name
        for name in names
    ):
        return "backend-nestjs"

    return "generic-security"


def resolve_prompt_path(input_prompt_path: str, stack: str, files: List[Dict[str, Any]]) -> str:
    if input_prompt_path:
        return input_prompt_path

    selected_stack = infer_stack(files) if stack == "auto" else stack
    return DEFAULT_PROMPTS.get(selected_stack, DEFAULT_PROMPTS["generic-security"])

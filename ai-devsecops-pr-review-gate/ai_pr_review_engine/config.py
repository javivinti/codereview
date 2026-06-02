import os
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Config:
    ai_provider: str
    ai_model: str
    ai_api_key: str
    ai_base_url: str
    prompt_path: str
    prompts_root: str
    stack: str
    comment_pr: bool
    fail_on_severity: str
    exclude_directories: List[str]
    max_files: int
    max_diff_chars: int
    include_pr_comments: bool
    custom_instructions: str
    enable_basic_filter: bool


def _bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _csv(value: str) -> List[str]:
    return [item.strip().strip("/") for item in (value or "").split(",") if item.strip()]


def load_config() -> Config:
    fail_on_severity = os.getenv("INPUT_FAIL_ON_SEVERITY", "never").strip().lower()
    if fail_on_severity not in {"critical", "high", "medium", "low", "never"}:
        raise ValueError("fail-on-severity must be one of: critical, high, medium, low, never")

    return Config(
        ai_provider=os.getenv("INPUT_AI_PROVIDER", "").strip().lower(),
        ai_model=os.getenv("INPUT_AI_MODEL", "").strip(),
        ai_api_key=os.getenv("INPUT_AI_API_KEY", "").strip(),
        ai_base_url=os.getenv("INPUT_AI_BASE_URL", "").strip().rstrip("/"),
        prompt_path=os.getenv("INPUT_PROMPT_PATH", "").strip(),
        prompts_root=os.getenv("AI_PROMPTS_ROOT", os.getcwd()).strip(),
        stack=os.getenv("INPUT_STACK", "auto").strip().lower(),
        comment_pr=_bool(os.getenv("INPUT_COMMENT_PR", "true"), True),
        fail_on_severity=fail_on_severity,
        exclude_directories=_csv(os.getenv("INPUT_EXCLUDE_DIRECTORIES", "node_modules,dist,build,vendor,.git,coverage")),
        max_files=int(os.getenv("INPUT_MAX_FILES", "80")),
        max_diff_chars=int(os.getenv("INPUT_MAX_DIFF_CHARS", "180000")),
        include_pr_comments=_bool(os.getenv("INPUT_INCLUDE_PR_COMMENTS", "true"), True),
        custom_instructions=os.getenv("INPUT_CUSTOM_INSTRUCTIONS", "").strip(),
        enable_basic_filter=_bool(os.getenv("INPUT_ENABLE_BASIC_FILTER", "true"), True),
    )

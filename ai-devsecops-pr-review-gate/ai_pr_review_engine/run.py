import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

from ai_pr_review_engine.config import load_config
from ai_pr_review_engine.github_client import GitHubClient
from ai_pr_review_engine.pr_context import build_pr_context, write_context_file
from ai_pr_review_engine.prompt_loader import load_prompt
from ai_pr_review_engine.prompt_selector import resolve_prompt_path
from ai_pr_review_engine.providers.factory import create_provider
from ai_pr_review_engine.response_parser import normalize_result, parse_jsonish
from ai_pr_review_engine.result_filter import filter_findings
from ai_pr_review_engine.review_prompt import SYSTEM_PROMPT, build_final_prompt
from ai_pr_review_engine.renderer import render_markdown, write_comment_file
from ai_pr_review_engine.severity_gate import should_fail


RESULTS_FILE = "ai-review-result.json"


def set_output(name: str, value: str) -> None:
    output = os.getenv("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as fh:
            fh.write(f"{name}={value}\n")


def write_json(path: str, payload: Dict[str, Any]) -> str:
    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def main() -> int:
    try:
        config = load_config()
        github = GitHubClient()

        pr = github.get_pr()
        files = github.list_pr_files()
        comments = github.list_issue_comments() if config.include_pr_comments else []

        metadata, pr_context = build_pr_context(
            repository=github.repository,
            pr=pr,
            files=files,
            comments=comments,
            excluded_dirs=config.exclude_directories,
            max_files=config.max_files,
            max_diff_chars=config.max_diff_chars,
            include_comments=config.include_pr_comments,
        )

        context_file = write_context_file(pr_context)

        prompt_path = resolve_prompt_path(
            input_prompt_path=config.prompt_path,
            stack=config.stack,
            files=files,
        )
        prompt_pack = load_prompt(config.prompts_root, prompt_path)

        provider_name = config.ai_provider or prompt_pack.metadata.get("provider", "").lower() or "mock"
        model_name = config.ai_model or prompt_pack.metadata.get("model", "") or "mock"

        base_url = config.ai_base_url
        if provider_name == "openai-compatible" and not base_url:
            base_url = prompt_pack.metadata.get("baseUrl", "") or prompt_pack.metadata.get("base_url", "")

        api_key = config.ai_api_key
        if provider_name == "mock":
            api_key = ""

        final_prompt = build_final_prompt(
            prompt_body=prompt_pack.body,
            pr_context=pr_context,
            custom_instructions=config.custom_instructions,
        )

        if metadata.get("changed_files_analyzed", 0) == 0:
            result = {
                "summary": "No analyzable textual diff was available for this Pull Request.",
                "impact_score": 1,
                "quality_score": "A",
                "findings": [],
                "positive_points": [],
                "critical_violations": [],
            }
        else:
            provider = create_provider(
                provider=provider_name,
                model=model_name,
                api_key=api_key,
                base_url=base_url,
            )
            raw_response = provider.complete(SYSTEM_PROMPT, final_prompt)
            result = normalize_result(parse_jsonish(raw_response))

        if config.enable_basic_filter:
            result["findings"] = filter_findings(result.get("findings", []))

        payload = {
            "repository": github.repository,
            "pull_request": metadata.get("pr_number"),
            "provider": provider_name,
            "model": model_name,
            "prompt_path": prompt_path,
            "metadata": metadata,
            "summary": result.get("summary"),
            "impact_score": result.get("impact_score"),
            "quality_score": result.get("quality_score"),
            "findings_count": len(result.get("findings", [])),
            "findings": result.get("findings", []),
            "positive_points": result.get("positive_points", []),
            "critical_violations": result.get("critical_violations", []),
        }

        results_file = write_json(RESULTS_FILE, payload)

        comment = render_markdown(
            result=result,
            metadata=metadata,
            provider=provider_name,
            model=model_name,
            prompt_path=prompt_path,
        )
        comment_file = write_comment_file(comment)

        if config.comment_pr:
            github.upsert_issue_comment(comment)

        set_output("findings_count", str(payload["findings_count"]))
        set_output("results_file", results_file)
        set_output("context_file", context_file)
        set_output("comment_file", comment_file)

        if should_fail(payload["findings"], config.fail_on_severity):
            print(f"Failing because threshold was met: {config.fail_on_severity}", file=sys.stderr)
            return 2

        return 0

    except Exception as exc:
        error_payload = {
            "error": str(exc),
            "findings_count": 0,
            "findings": [],
        }
        write_json(RESULTS_FILE, error_payload)
        set_output("findings_count", "0")
        set_output("results_file", RESULTS_FILE)
        print(f"AI DevSecOps PR Review Gate failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

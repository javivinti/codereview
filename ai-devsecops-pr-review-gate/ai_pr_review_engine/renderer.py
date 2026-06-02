from pathlib import Path
from typing import Any, Dict, List


SEVERITY_ICON = {
    "critical": "🚨",
    "high": "🔴",
    "medium": "🟠",
    "low": "🟡",
    "info": "ℹ️",
}


def render_markdown(result: Dict[str, Any], metadata: Dict[str, Any], provider: str, model: str, prompt_path: str) -> str:
    findings: List[Dict[str, Any]] = result.get("findings", [])
    lines: List[str] = [
        "## 🤖 AI DevSecOps PR Review Gate",
        "",
        result.get("summary", "AI PR review completed."),
        "",
        "### Review metadata",
        "",
        f"- **Provider:** `{provider}`",
        f"- **Model:** `{model}`",
        f"- **Prompt:** `{prompt_path}`",
        f"- **Changed files analyzed:** `{metadata.get('changed_files_analyzed')}` / `{metadata.get('changed_files_total')}`",
        f"- **Impact score:** `{result.get('impact_score', 'N/A')}`",
        f"- **Quality score:** `{result.get('quality_score', 'N/A')}`",
        "",
    ]

    skipped = metadata.get("skipped") or []
    if skipped:
        lines.extend(["<details>", "<summary>Skipped files</summary>", ""])
        lines.extend(f"- `{item}`" for item in skipped)
        lines.extend(["", "</details>", ""])

    critical_violations = result.get("critical_violations") or []
    if critical_violations:
        lines.extend(["### Critical violations", ""])
        lines.extend(f"- {item}" for item in critical_violations)
        lines.append("")

    if not findings:
        lines.extend(["✅ No actionable findings detected in this Pull Request context.", ""])
    else:
        lines.extend([f"### Findings ({len(findings)})", ""])

        for index, finding in enumerate(findings, start=1):
            severity = finding.get("severity", "info")
            icon = SEVERITY_ICON.get(severity, "ℹ️")
            location = f"`{finding.get('file', '')}`"
            if finding.get("line"):
                location += f":{finding.get('line')}"

            lines.extend(
                [
                    f"#### {index}. {icon} {finding.get('title', 'AI review finding')}",
                    "",
                    f"- **Severity:** `{severity}`",
                    f"- **Confidence:** `{finding.get('confidence', 'medium')}`",
                    f"- **Category:** `{finding.get('category', '')}`",
                    f"- **Location:** {location}",
                    f"- **CWE:** `{finding.get('cwe') or 'N/A'}`",
                    "",
                    f"**Description:** {finding.get('description', '')}",
                    "",
                    f"**Recommendation:** {finding.get('recommendation', '')}",
                    "",
                ]
            )

    positive_points = result.get("positive_points") or []
    if positive_points:
        lines.extend(["### Positive points", ""])
        lines.extend(f"- {item}" for item in positive_points)
        lines.append("")

    lines.extend(
        [
            "---",
            "_AI-assisted review. Validate findings before merging. This tool does not replace SAST, SCA, IaC or human review._",
            "",
        ]
    )

    return "\n".join(lines)


def write_comment_file(comment: str, path: str = "ai-review-comment.md") -> str:
    Path(path).write_text(comment, encoding="utf-8")
    return path

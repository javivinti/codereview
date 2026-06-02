from pathlib import Path
from typing import Any, Dict, List, Tuple


def is_excluded(path: str, excluded_dirs: List[str]) -> bool:
    clean = path.strip("/")
    for directory in excluded_dirs:
        d = directory.strip("/")
        if not d:
            continue
        if clean == d or clean.startswith(d + "/"):
            return True
    return False


def _comment_to_markdown(comment: Dict[str, Any]) -> str:
    user = comment.get("user", {}).get("login", "unknown")
    body = comment.get("body", "")
    created_at = comment.get("created_at", "")
    return f"- {created_at} @{user}: {body}"


def build_pr_context(
    repository: str,
    pr: Dict[str, Any],
    files: List[Dict[str, Any]],
    comments: List[Dict[str, Any]],
    excluded_dirs: List[str],
    max_files: int,
    max_diff_chars: int,
    include_comments: bool,
) -> Tuple[Dict[str, Any], str]:
    selected: List[Dict[str, Any]] = []
    skipped: List[str] = []

    for f in files:
        filename = f.get("filename", "")
        patch = f.get("patch") or ""

        if is_excluded(filename, excluded_dirs):
            skipped.append(f"{filename} (excluded directory)")
            continue

        if not patch:
            skipped.append(f"{filename} (no textual patch available)")
            continue

        selected.append(f)
        if len(selected) >= max_files:
            break

    diff_blocks: List[str] = []
    current_chars = 0

    for f in selected:
        filename = f.get("filename", "")
        status = f.get("status", "")
        patch = f.get("patch") or ""

        block = (
            f"\n## File: {filename}\n\n"
            f"- Status: {status}\n"
            f"- Additions: {f.get('additions', 0)}\n"
            f"- Deletions: {f.get('deletions', 0)}\n"
            f"- Changes: {f.get('changes', 0)}\n\n"
            "```diff\n"
            f"{patch}\n"
            "```\n"
        )

        if current_chars + len(block) > max_diff_chars:
            skipped.append(f"{filename} (max diff size reached)")
            continue

        diff_blocks.append(block)
        current_chars += len(block)

    metadata = {
        "repository": repository,
        "pr_number": pr.get("number"),
        "title": pr.get("title"),
        "author": pr.get("user", {}).get("login"),
        "base_ref": pr.get("base", {}).get("ref"),
        "head_ref": pr.get("head", {}).get("ref"),
        "changed_files_total": len(files),
        "changed_files_analyzed": len(selected),
        "skipped": skipped,
    }

    context_lines: List[str] = [
        "# Pull Request Context",
        "",
        "## Metadata",
        "",
        f"- Repository: {repository}",
        f"- Pull Request: #{pr.get('number')}",
        f"- Title: {pr.get('title')}",
        f"- Author: {pr.get('user', {}).get('login')}",
        f"- Base branch: {pr.get('base', {}).get('ref')}",
        f"- Head branch: {pr.get('head', {}).get('ref')}",
        f"- Changed files total: {len(files)}",
        f"- Changed files analyzed: {len(selected)}",
        "",
        "## Pull Request Description",
        "",
        pr.get("body") or "(empty)",
        "",
        "## Changed Files",
        "",
    ]

    for f in selected:
        context_lines.append(f"- `{f.get('filename')}` ({f.get('status')})")

    if skipped:
        context_lines.extend(["", "## Skipped Files", ""])
        for item in skipped:
            context_lines.append(f"- {item}")

    if include_comments:
        context_lines.extend(["", "## Existing PR Comments", ""])
        if comments:
            context_lines.extend(_comment_to_markdown(c) for c in comments[-30:])
        else:
            context_lines.append("(no comments)")

    context_lines.extend(["", "## Diffs", ""])
    context_lines.extend(diff_blocks)

    return metadata, "\n".join(context_lines)


def write_context_file(content: str, path: str = "pr_context.md") -> str:
    Path(path).write_text(content, encoding="utf-8")
    return path

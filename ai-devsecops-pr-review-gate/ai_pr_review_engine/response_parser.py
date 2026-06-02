import json
import re
from typing import Any, Dict, List


def parse_jsonish(text: str) -> Dict[str, Any]:
    raw = text.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    fenced = re.search(r"```(?:json)?\s*(.*?)```", raw, re.DOTALL | re.IGNORECASE)
    if fenced:
        try:
            return json.loads(fenced.group(1).strip())
        except json.JSONDecodeError:
            pass

    start = raw.find("{")
    end = raw.rfind("}")

    if start != -1 and end != -1 and end > start:
        return json.loads(raw[start : end + 1])

    # Fallback for old prompt style with Impact/Calidad
    return parse_legacy_markdown(raw)


def parse_legacy_markdown(text: str) -> Dict[str, Any]:
    impact = None
    quality = None

    impact_match = re.search(r"impacto?\**\s*:\s*(\d)", text, re.IGNORECASE)
    if impact_match:
        impact = int(impact_match.group(1))

    quality_match = re.search(r"calidad\**\s*:\s*([A-E])", text, re.IGNORECASE)
    if quality_match:
        quality = quality_match.group(1).upper()

    return {
        "summary": text[:1500],
        "impact_score": impact,
        "quality_score": quality,
        "findings": [],
        "positive_points": [],
        "critical_violations": [],
        "raw_markdown_fallback": True,
    }


def normalize_result(data: Dict[str, Any]) -> Dict[str, Any]:
    findings = data.get("findings") or []
    if not isinstance(findings, list):
        findings = []

    normalized_findings: List[Dict[str, Any]] = []
    for item in findings:
        if not isinstance(item, dict):
            continue

        normalized_findings.append(
            {
                "title": str(item.get("title") or "AI review finding"),
                "severity": str(item.get("severity") or "info").lower(),
                "confidence": str(item.get("confidence") or "medium").lower(),
                "file": str(item.get("file") or ""),
                "line": item.get("line"),
                "category": str(item.get("category") or ""),
                "description": str(item.get("description") or ""),
                "recommendation": str(item.get("recommendation") or ""),
                "cwe": str(item.get("cwe") or ""),
            }
        )

    return {
        "summary": str(data.get("summary") or "AI PR review completed."),
        "impact_score": data.get("impact_score"),
        "quality_score": data.get("quality_score"),
        "findings": normalized_findings,
        "positive_points": data.get("positive_points") or [],
        "critical_violations": data.get("critical_violations") or [],
        "raw_markdown_fallback": bool(data.get("raw_markdown_fallback", False)),
    }

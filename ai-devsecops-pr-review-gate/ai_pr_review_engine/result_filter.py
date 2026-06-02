from typing import Any, Dict, List


LOW_VALUE_TERMS = [
    "rate limit",
    "rate limiting",
    "denial of service",
    "dos",
    "generic input validation",
    "best practice",
    "consider",
    "could potentially",
]


def _joined_text(finding: Dict[str, Any]) -> str:
    return " ".join(
        str(finding.get(field, ""))
        for field in ["title", "category", "description", "recommendation"]
    ).lower()


def filter_findings(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    filtered: List[Dict[str, Any]] = []

    for finding in findings:
        severity = str(finding.get("severity", "info")).lower()
        confidence = str(finding.get("confidence", "medium")).lower()
        text = _joined_text(finding)

        if severity == "info":
            continue

        if not finding.get("file"):
            continue

        if confidence == "low" and any(term in text for term in LOW_VALUE_TERMS):
            continue

        filtered.append(finding)

    return filtered

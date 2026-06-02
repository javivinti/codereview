from typing import Any, Dict, List

ORDER = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
    "info": 0,
}


def should_fail(findings: List[Dict[str, Any]], threshold: str) -> bool:
    if threshold == "never":
        return False

    threshold_score = ORDER[threshold]
    return any(
        ORDER.get(str(finding.get("severity", "info")).lower(), 0) >= threshold_score
        for finding in findings
    )

from ai_pr_review_engine.response_parser import normalize_result, parse_jsonish


def test_parse_jsonish():
    result = parse_jsonish('{"summary":"ok","findings":[]}')
    assert result["summary"] == "ok"


def test_normalize():
    result = normalize_result({"summary": "ok", "findings": [{"severity": "HIGH", "title": "x"}]})
    assert result["findings"][0]["severity"] == "high"

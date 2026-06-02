from ai_pr_review_engine.prompt_selector import infer_stack


def test_infer_terraform():
    assert infer_stack([{"filename": "infra/main.tf"}]) == "terraform"


def test_infer_go():
    assert infer_stack([{"filename": "cmd/api/main.go"}]) == "backend-go"


def test_infer_nestjs():
    assert infer_stack([{"filename": "src/users/user.controller.ts"}]) == "backend-nestjs"

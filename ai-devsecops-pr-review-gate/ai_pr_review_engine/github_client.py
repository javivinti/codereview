import json
import os
from pathlib import Path
from typing import Any, Dict, List

import requests


class GitHubClient:
    def __init__(self) -> None:
        self.token = os.getenv("GITHUB_TOKEN")
        self.repository = os.getenv("GITHUB_REPOSITORY")
        self.event_path = os.getenv("GITHUB_EVENT_PATH")

        if not self.token:
            raise ValueError("GITHUB_TOKEN is required")
        if not self.repository:
            raise ValueError("GITHUB_REPOSITORY is required")
        if not self.event_path:
            raise ValueError("GITHUB_EVENT_PATH is required")

        self.api = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        self.event = json.loads(Path(self.event_path).read_text(encoding="utf-8"))
        pull_request = self.event.get("pull_request")
        if not pull_request:
            raise ValueError("This action currently supports pull_request events only")

        self.pr_number = int(pull_request["number"])

    def _request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        response = requests.request(method, url, headers=self.headers, timeout=45, **kwargs)
        response.raise_for_status()
        return response

    def get_pr(self) -> Dict[str, Any]:
        url = f"{self.api}/repos/{self.repository}/pulls/{self.pr_number}"
        return self._request("GET", url).json()

    def list_pr_files(self) -> List[Dict[str, Any]]:
        files: List[Dict[str, Any]] = []
        page = 1

        while True:
            url = f"{self.api}/repos/{self.repository}/pulls/{self.pr_number}/files"
            batch = self._request("GET", url, params={"per_page": 100, "page": page}).json()
            files.extend(batch)
            if len(batch) < 100:
                break
            page += 1

        return files

    def list_issue_comments(self) -> List[Dict[str, Any]]:
        comments: List[Dict[str, Any]] = []
        page = 1

        while True:
            url = f"{self.api}/repos/{self.repository}/issues/{self.pr_number}/comments"
            batch = self._request("GET", url, params={"per_page": 100, "page": page}).json()
            comments.extend(batch)
            if len(batch) < 100:
                break
            page += 1

        return comments

    def upsert_issue_comment(self, body: str, marker: str = "<!-- ai-devsecops-pr-review-gate -->") -> None:
        full_body = f"{marker}\n{body}"
        existing = None

        for comment in self.list_issue_comments():
            if marker in comment.get("body", ""):
                existing = comment
                break

        if existing:
            self._request("PATCH", existing["url"], json={"body": full_body})
            return

        url = f"{self.api}/repos/{self.repository}/issues/{self.pr_number}/comments"
        self._request("POST", url, json={"body": full_body})

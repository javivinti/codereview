from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple


@dataclass
class PromptPack:
    path: str
    metadata: Dict[str, str]
    body: str


def parse_front_matter(text: str) -> Tuple[Dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text

    metadata: Dict[str, str] = {}
    end_index = None

    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_index = i
            break

        line = lines[i]
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip('"').strip("'")

    if end_index is None:
        return {}, text

    body = "\n".join(lines[end_index + 1 :]).strip()
    return metadata, body


def load_prompt(prompt_root: str, prompt_path: str) -> PromptPack:
    root = Path(prompt_root).resolve()
    candidate = (root / prompt_path).resolve()

    if not str(candidate).startswith(str(root)):
        raise ValueError(f"Prompt path escapes prompt root: {prompt_path}")

    if not candidate.exists():
        raise FileNotFoundError(f"Prompt file not found: {candidate}")

    text = candidate.read_text(encoding="utf-8")
    metadata, body = parse_front_matter(text)
    return PromptPack(path=str(candidate), metadata=metadata, body=body)

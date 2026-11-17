from pathlib import Path
from typing import TypedDict


class StaticLinkDescription(TypedDict):
    rel: str
    filepath: Path


STATIC_LINKS: list[StaticLinkDescription] = [
    {"rel": "agents", "filepath": Path(__file__).parent / "AGENTS.md"},
    {"rel": "describedby", "filepath": Path(__file__).parent / "README.md"},
]

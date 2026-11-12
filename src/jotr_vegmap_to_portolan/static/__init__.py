from pathlib import Path
from typing import TypedDict


class StaticAssetDescription(TypedDict):
    rel: str
    filepath: Path


STATIC_ASSETS: list[StaticAssetDescription] = [
    {"rel": "agents", "filepath": Path(__file__).parent / "AGENTS.md"},
    {"rel": "describedby", "filepath": Path(__file__).parent / "README.md"},
]

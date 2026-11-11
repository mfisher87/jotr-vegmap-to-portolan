from pathlib import Path

STATIC_ASSETS = [
    {"rel": "agents", "filepath": Path(__file__).parent / "AGENTS.md"},
    {"rel": "describedby", "filepath": Path(__file__).parent / "README.md"},
]

from pathlib import Path
from typing import TypedDict

import pystac

from jotr_vegmap_to_portolan._types import CollectionName


class StaticLinkDescription(TypedDict):
    rel: str
    filepath: Path


class StaticAssetDescription(TypedDict):
    key: str
    filepath: Path
    title: str
    media_type: str | pystac.MediaType
    roles: list[str]


STATIC_LINKS: list[StaticLinkDescription] = [
    {"rel": "agents", "filepath": Path(__file__).parent / "AGENTS.md"},
    {"rel": "describedby", "filepath": Path(__file__).parent / "README.md"},
]

STATIC_ASSETS: dict[CollectionName, list[StaticAssetDescription]] = {
    "park-boundary": [
        {
            "key": "styles/default",
            "filepath": Path(__file__).parent / "park-boundary.style.json",
            "title": "Default style for park boundary",
            "media_type": "application/vnd.mapbox.style+json",
            "roles": ["style", "default"],
        },
    ],
    "vegetation-map": [
        {
            "key": "styles/default",
            "filepath": Path(__file__).parent / "vegetation-map.style.json",
            "title": "Default style for vegetation map",
            "media_type": "application/vnd.mapbox.style+json",
            "roles": ["style", "default"],
        },
    ],
}

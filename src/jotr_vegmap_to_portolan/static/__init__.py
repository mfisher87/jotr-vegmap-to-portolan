from pathlib import Path
from typing import TypedDict

import pystac

from jotr_vegmap_to_portolan._types import CollectionName

STATIC_ASSETS_DIR = Path(__file__).parent


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
    {"rel": "agents", "filepath": STATIC_ASSETS_DIR / "AGENTS.md"},
    {"rel": "describedby", "filepath": STATIC_ASSETS_DIR / "README.md"},
]

STATIC_ASSETS: dict[CollectionName, list[StaticAssetDescription]] = {
    "park-boundary": [
        {
            "key": "styles/default",
            "filepath": STATIC_ASSETS_DIR / "park-boundary.style.json",
            "title": "Default style for park boundary",
            "media_type": "application/vnd.mapbox.style+json",
            "roles": ["style", "default"],
        },
    ],
    "vegetation-map": [
        {
            "key": "styles/default",
            "filepath": STATIC_ASSETS_DIR / "vegetation-map.style.json",
            "title": "Default style for vegetation map",
            "media_type": "application/vnd.mapbox.style+json",
            "roles": ["style", "default"],
        },
    ],
}


def default_style_filepath(collection_name: CollectionName) -> Path:
    """Get the default MapLibre style for a collection."""
    for asset in STATIC_ASSETS[collection_name]:
        if {"style", "default"}.issubset(set(asset["roles"])):
            return asset["filepath"]
    msg = f"no default style registered for {collection_name}"
    raise RuntimeError(msg)

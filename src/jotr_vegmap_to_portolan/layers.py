from typing import Literal, TypedDict

from jotr_vegmap_to_portolan._types import CollectionName


class DataLayer(TypedDict):
    from_gpd_layer: Literal["JOTR_Park_Boundary", "JOTR_VegPolys"]
    to_id: CollectionName
    title: str


# A Geodatabase contains tables that it calls "layers"
DATA_LAYERS: list[DataLayer] = [
    {
        "from_gpd_layer": "JOTR_Park_Boundary",
        "to_id": "park-boundary",  # TODO: Type
        "title": "Joshua Tree National Park boundary",
    },
    {
        "from_gpd_layer": "JOTR_VegPolys",
        "to_id": "vegetation-map",
        "title": "Joshua Tree National Park vegetation map",
    },
]

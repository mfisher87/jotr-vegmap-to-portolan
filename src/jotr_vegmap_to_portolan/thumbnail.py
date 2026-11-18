import json
from pathlib import Path
from typing import Any

import geopandas as gpd
import matplotlib as mpl
from matplotlib import pyplot as plt

mpl.use("Agg")  # no display in CI

_SIZE_INCHES = 3.0
_DPI = 96


def generate_thumbnail(
    *,
    geodataframe: gpd.GeoDataFrame,
    style_filepath: Path,
    thumbnail_filepath: Path,
) -> None:
    """Render the layer as a small PNG using its default style.

    Rashid's PTL-VIZ-001 fix hint suggests "a thumbnail generated from the collection's
    default styling".
    """
    figure, axes = plt.subplots(figsize=(_SIZE_INCHES, _SIZE_INCHES))
    geodataframe.to_crs("EPSG:3857").plot(
        ax=axes,
        **_plot_kwargs_from_maplibre_style(style_filepath),
    )

    axes.set_axis_off()
    figure.savefig(
        thumbnail_filepath,
        dpi=_DPI,
        bbox_inches="tight",
        pad_inches=0,
        transparent=True,
    )
    plt.close(figure)


def _plot_kwargs_from_maplibre_style(style_filepath: Path) -> dict[str, Any]:
    """GeoPandas plot keywords for a MapLibre style.

    First layer is used.
    """
    style_layer = json.loads(style_filepath.read_text(encoding="utf-8"))["layers"][0]
    paint = style_layer["paint"]
    if style_layer["type"] == "line":
        return {
            "facecolor": "none",
            "edgecolor": paint["line-color"],
            "linewidth": paint["line-width"],
        }
    return {
        "facecolor": paint["fill-color"],
        "alpha": paint.get("fill-opacity", 1.0),
        "edgecolor": paint.get("fill-outline-color", "none"),
        "linewidth": 0.2,
    }

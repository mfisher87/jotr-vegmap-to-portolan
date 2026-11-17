from pathlib import Path

import geopandas as gpd
import h3.api.basic_int as h3
import pandas as pd
import pystac

from jotr_vegmap_to_portolan.dirs import ASSETS_DIRNAME, PARQUET_H3_DIRNAME
from jotr_vegmap_to_portolan.exceptions import TypeguardError

H3_RES_NATIVE = 10
H3_RES_PARENTS = (9, 8, 0)


def generate_parquet_h3(
    *,
    parqueted_stac_filepath: Path,
    target_dir: Path,
    tmpdir: Path,
) -> Path:
    destination_dir = tmpdir / PARQUET_H3_DIRNAME
    assets_dir = target_dir / ASSETS_DIRNAME

    input_stac = pystac.Catalog.from_file(parqueted_stac_filepath)

    catalog = input_stac.full_copy()
    catalog.id = "jotr-vegmap-parquet-h3"
    catalog.title = "JOTR vegetation map"
    catalog.description = (
        "Contains vegetation map and park boundary. Now with H3 hexed data!"
    )

    for collection_name in ["park-boundary", "vegetation-map"]:
        collection = catalog.get_child(collection_name)
        if not isinstance(collection, pystac.Collection):
            raise TypeguardError

        parquet_asset = collection.assets["parquet"]

        gdf = gpd.read_parquet(parquet_asset.href)
        gdf = gdf.to_crs("EPSG:4326")
        without_geom = gdf.drop(columns=gdf.geometry.name)

        cells_per_feature = [
            h3.geo_to_cells(geometry, H3_RES_NATIVE) for geometry in gdf.geometry
        ]

        native_column = f"h{H3_RES_NATIVE}"

        hex_table = without_geom.loc[
            without_geom.index.repeat([len(cells) for cells in cells_per_feature])
        ].reset_index(drop=True)
        hex_table[native_column] = pd.Series(
            [cell for cells in cells_per_feature for cell in cells],
            dtype="uint64",
        )
        for parent_resolution in H3_RES_PARENTS:
            hex_table[f"h{parent_resolution}"] = pd.Series(
                [
                    h3.cell_to_parent(cell, parent_resolution)
                    for cell in hex_table[native_column]
                ],
                dtype="uint64",
            )

        parquet_h3_path = assets_dir / f"{collection.id}-h3.parquet"
        hex_table.to_parquet(parquet_h3_path)
        collection.add_asset(
            key="parquet-h3",
            asset=pystac.Asset(
                href=str(parquet_h3_path),
                media_type=pystac.MediaType.PARQUET,
                roles=["data"],
            ),
        )

    catalog.normalize_hrefs(str(destination_dir))
    catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)

    href = catalog.get_self_href()
    if href is None:
        raise TypeguardError

    return Path(href)

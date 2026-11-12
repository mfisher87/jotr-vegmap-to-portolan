import datetime
from pathlib import Path

import geopandas as gpd
import pystac

from jotr_vegmap_to_portolan.dirs import ASSETS_DIRNAME, PARQUET_DIRNAME
from jotr_vegmap_to_portolan.download import DOWNLOAD_ITEM_ID, DOWNLOAD_ASSET_KEY
from jotr_vegmap_to_portolan.exceptions import TypeguardException
from jotr_vegmap_to_portolan.layers import DATA_LAYERS


def generate_parquet(*, input_data_stac_filepath: Path, tmpdir: Path) -> Path:
    destination_dir = tmpdir / PARQUET_DIRNAME
    assets_dir = tmpdir / ASSETS_DIRNAME

    input_stac = pystac.Catalog.from_file(input_data_stac_filepath)

    gdb_item = next(input_stac.get_items(DOWNLOAD_ITEM_ID), None)
    if gdb_item is None:
        raise TypeguardException

    gdb_path = Path(gdb_item.assets[DOWNLOAD_ASSET_KEY].href)

    catalog = pystac.Catalog(
        id="jotr-vegmap-parquet",
        description="JOTR vegetation map in Parquet",
    )

    items: list[pystac.Item] = []
    for data_layer in DATA_LAYERS:
        parquet_path = assets_dir / f"{data_layer['to_asset_id']}.parquet"

        gdf = gpd.read_file(gdb_path, layer=data_layer["from_gpd_layer"])
        gdf.to_parquet(parquet_path)

        item = pystac.Item(
            id=data_layer["to_asset_id"],
            geometry=None,
            bbox=gdf.to_crs("EPSG:4326").total_bounds.tolist(),
            datetime=datetime.datetime.now(),  # Probably bad but whatever
            properties={},
        )
        item.add_asset(
            key="parquet",
            asset=pystac.Asset(
                href=str(parquet_path),
                media_type=pystac.MediaType.PARQUET,
                roles=["data"],
            ),
        )
        items.append(item)

    collection = pystac.Collection(
        id="jotr-vegmap",
        title="JOTR vegetation map & park boundary",
        description="JOTR vegetation map & park boundary",
        extent=pystac.Extent.from_items(items),
        providers=[
            pystac.Provider(
                name="Schmidt Center for Data Science & Environment",
                url="https://dse.berkeley.edu/",
                description="Processed source data in to H3 DGGS",
                roles=[pystac.ProviderRole.PROCESSOR],
            ),
            pystac.Provider(
                name="National Park Service",
                url="https://www.nps.gov",
                description="Original data provider",
                roles=[
                    pystac.ProviderRole.PRODUCER,
                    pystac.ProviderRole.HOST,
                ],
            ),
        ],
        # Unclear. License field on portal is empty. Data is public domain.
        license="CC0-1.0",
    )
    catalog.add_child(collection, title=collection.description)

    for item in items:
        collection.add_item(item, title=data_layer["title"])

    catalog.normalize_hrefs(str(destination_dir))
    catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)

    href = catalog.get_self_href()
    if href is None:
        raise TypeguardException

    return Path(href)

from pathlib import Path

import geopandas as gpd
import pyogrio
import pystac

from jotr_vegmap_to_portolan.dirs import PMTILES_DIRNAME
from jotr_vegmap_to_portolan.exceptions import TypeguardError


def generate_pmtiles(*, parqueted_stac_filepath: Path, tmpdir: Path) -> Path:
    destination_dir = tmpdir / PMTILES_DIRNAME

    input_stac = pystac.Catalog.from_file(parqueted_stac_filepath)

    catalog = input_stac.full_copy()
    catalog.id = "jotr-vegmap-parquet-and-pmtiles"
    catalog.description = "JOTR vegetation map in Parquet and PMTiles"

    for item in next(iter(catalog.get_children())).get_items():
        parquet_asset = next(iter(item.get_assets().values()))
        parquet_path = Path(parquet_asset.href)
        pmtiles_path = parquet_path.parent / f"{parquet_path.stem}.pmtiles"
        gdf = gpd.read_parquet(parquet_path)

        pyogrio.write_dataframe(
            gdf,
            pmtiles_path,
            driver="PMTiles",
            layer=item.id,
            MINZOOM="12",  # TODO: Figure this out programmatically
            MAXZOOM="14",
        )
        item.add_asset(
            key="pmtiles",
            asset=pystac.Asset(
                href=str(pmtiles_path),
                media_type=pystac.MediaType.VND_PMTILES,
                roles=["visual"],
            ),
        )

    catalog.normalize_hrefs(str(destination_dir))
    catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)

    href = catalog.get_self_href()
    if href is None:
        raise TypeguardError

    return Path(href)

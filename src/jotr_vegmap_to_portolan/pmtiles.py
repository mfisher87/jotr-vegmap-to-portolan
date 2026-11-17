from pathlib import Path

import geopandas as gpd
import pyogrio
import pystac

from jotr_vegmap_to_portolan.dirs import PMTILES_DIRNAME
from jotr_vegmap_to_portolan.exceptions import TypeguardError


def generate_pmtiles(*, h3d_stac_filepath: Path, tmpdir: Path) -> Path:
    destination_dir = tmpdir / PMTILES_DIRNAME

    input_stac = pystac.Catalog.from_file(h3d_stac_filepath)

    catalog = input_stac.full_copy()
    catalog.id = "jotr-vegmap-parquet-and-pmtiles"
    catalog.description = "JOTR vegetation map in Parquet and PMTiles"

    for collection in catalog.get_children():
        if not isinstance(collection, pystac.Collection):
            raise TypeguardError

        parquet_asset = collection.assets["parquet"]
        parquet_path = Path(parquet_asset.href)
        pmtiles_path = parquet_path.parent / f"{parquet_path.stem}.pmtiles"
        gdf = gpd.read_parquet(parquet_path)

        pmtiles_path.unlink(missing_ok=True)
        pyogrio.write_dataframe(
            gdf,
            pmtiles_path,
            driver="PMTiles",
            layer=collection.id,
            MINZOOM="8",  # TODO: Figure this out programmatically
            MAXZOOM="14",
        )
        pmtiles_asset = pystac.Asset(
            href=str(pmtiles_path),
            media_type=pystac.MediaType.VND_PMTILES,
            roles=["visual"],
        )

        collection.add_asset(key="pmtiles", asset=pmtiles_asset)
        collection.add_link(
            pystac.Link(
                rel="pmtiles",
                target=pmtiles_asset.href,
                media_type=pystac.MediaType.VND_PMTILES,
            ),
        )

        collection.stac_extensions.append(
            "https://stac-extensions.github.io/web-map-links/v1.3.0/schema.json",
        )

    catalog.normalize_hrefs(str(destination_dir))
    catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)

    href = catalog.get_self_href()
    if href is None:
        raise TypeguardError

    return Path(href)

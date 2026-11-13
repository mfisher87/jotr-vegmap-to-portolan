import shutil
from pathlib import Path

import pystac
from rashid import validate

from jotr_vegmap_to_portolan.exceptions import TypeguardError, ValidationError
from jotr_vegmap_to_portolan.static import STATIC_ASSETS


def generate_portolan(
    *,
    pmtiled_stac_filepath: Path,
    target_dir: Path,
) -> Path:
    input_stac = pystac.Catalog.from_file(pmtiled_stac_filepath)

    target_dir.mkdir(parents=True, exist_ok=True)

    catalog = input_stac.full_copy()
    catalog.id = "jotr-vegmap-portolan"
    catalog.title = "JOTR vegetation map"
    catalog.description = (
        "Contains vegetation map and park boundary. Portolan compliant!"
    )

    # Future steps depend on the catalog having the correct hrefs -- we'll need to do
    # this again when we're done updating the catalog.
    catalog.normalize_hrefs(str(target_dir))
    catalog.make_all_asset_hrefs_relative()
    catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)

    add_portolan_extension(catalog=catalog)
    add_static_assets(catalog=catalog)

    catalog.normalize_hrefs(str(target_dir))
    catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)

    catalog_href = catalog.get_self_href()
    if catalog_href is None:
        raise TypeguardError

    report = validate(catalog_href)

    for finding in report.errors:
        print(finding.message)

    if report.errors:
        raise ValidationError

    return target_dir


def add_portolan_extension(*, catalog: pystac.Catalog) -> None:
    portolan_schema_url = "https://schemas.portolan-sdi.org/portolan/v0.2.0/schema.json"

    catalog.stac_extensions.append(portolan_schema_url)

    # WARNING: Assumes a single-collection catalog
    collection = next(iter(catalog.get_children()))
    collection.stac_extensions.append(portolan_schema_url)


def add_static_assets(*, catalog: pystac.Catalog) -> None:
    """Add README.md and AGENTS.md to catalog.

    These aren't "assets" in the STAC sense.
    """
    # WARNING: Assumes a single-collection catalog
    collection = next(iter(catalog.get_children()))

    for asset in STATIC_ASSETS:
        for entity in [catalog, collection]:
            target_dir = Path(entity.self_href).parent
            target_filepath = target_dir / asset["filepath"].name
            shutil.copy(asset["filepath"], target_filepath)
            entity.add_link(
                pystac.Link(
                    rel=asset["rel"],
                    target=str(target_filepath.relative_to(target_dir)),
                    media_type="text/markdown",
                    title=target_filepath.name,
                ),
            )

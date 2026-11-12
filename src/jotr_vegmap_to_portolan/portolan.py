import shutil
from pathlib import Path

import pystac
from rashid import validate

from jotr_vegmap_to_portolan.dirs import PORTOLAN_DIRNAME
from jotr_vegmap_to_portolan.exceptions import ValidationException
from jotr_vegmap_to_portolan.static import STATIC_ASSETS


def generate_portolan(*, pmtiled_stac_filepath: Path, tmpdir: Path) -> Path:
    destination_dir = tmpdir / PORTOLAN_DIRNAME
    input_stac = pystac.Catalog.from_file(pmtiled_stac_filepath)

    destination_dir.mkdir()

    catalog = input_stac.full_copy()
    catalog.id = "jotr-vegmap-portolan"
    catalog.title = "JOTR vegetation map"
    catalog.description = (
        "Contains vegetation map and park boundary. Portolan compliant!"
    )

    # Future steps depend on the catalog having the correct hrefs -- we'll need to do
    # this again when we're done updating the catalog.
    catalog.normalize_hrefs(str(destination_dir))
    catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)

    add_static_assets(catalog=catalog)

    catalog.normalize_hrefs(str(destination_dir))
    catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)
    report = validate(catalog.get_self_href())

    for finding in report.errors:
        print(finding.message)

    if report.errors:
        raise ValidationException


def add_static_assets(*, catalog: pystac.Catalog) -> None:
    """Add README.md and AGENTS.md to catalog.

    These aren't "assets" in the STAC sense.
    """
    # WARNING: Assumes a single collection catalog
    collection = next(catalog.get_children())

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
                )
            )

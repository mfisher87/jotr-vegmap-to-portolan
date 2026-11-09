import datetime
import tempfile
import urllib.request
import zipfile
from contextlib import contextmanager
from pathlib import Path

import pystac

from jotr_vegmap_to_portolan.dirs import INPUT_DATA_DIRNAME

DOWNLOAD_URL = "https://irma.nps.gov/DataStore/DownloadFile/612199"
DOWNLOAD_FILENAME = "jotr_vegmap_gdb.zip"


@contextmanager
def download_data() -> Path:
    with tempfile.TemporaryDirectory() as destination_dir:
        destination_filepath = Path(destination_dir) / DOWNLOAD_FILENAME

        req = urllib.request.Request(url=DOWNLOAD_URL)
        with urllib.request.urlopen(req) as response:
            destination_filepath.write_bytes(response.read())

        yield destination_filepath


def download_and_unzip_data(*, tmpdir: Path) -> Path:
    destination_dir = tmpdir / INPUT_DATA_DIRNAME

    with (
        download_data() as downloaded,
        zipfile.ZipFile(downloaded, "r") as da_zip,
    ):
        da_zip.extractall(destination_dir)

    return destination_dir / "jotrgeodata" / "jotrgeodata.gdb"


def get_input_data(*, tmpdir: Path) -> pystac.Catalog:
    destination_dir = tmpdir / INPUT_DATA_DIRNAME
    gdb_dir = download_and_unzip_data(tmpdir=tmpdir)

    catalog = pystac.Catalog(
        id="jotr-vegmap-gdb",
        description="Source geodatabase of JOTR vegetation map",
    )
    item = pystac.Item(
        id="jotr-park-boundary-gdb",
        geometry=None,
        bbox=None,
        datetime=datetime.datetime.utcnow(),
        properties={},
    )
    item.add_asset(
        key="gdb",
        asset=pystac.Asset(
            href=str(gdb_dir),
            # This feels like nonsense -- assets are usually not ... directories.
            media_type="application/x-dir-geodatabase",
        ),
    )
    catalog.add_item(item)

    catalog.normalize_hrefs(str(destination_dir))
    catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)
    return catalog.get_self_href()

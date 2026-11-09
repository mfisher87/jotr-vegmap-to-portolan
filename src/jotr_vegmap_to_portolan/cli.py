import tempfile
from pathlib import Path

import typer
from rich import print as rprint

from jotr_vegmap_to_portolan.dirs import ASSETS_DIRNAME
from jotr_vegmap_to_portolan.download import get_input_data
from jotr_vegmap_to_portolan.parquet import generate_parquet
from jotr_vegmap_to_portolan.pmtiles import generate_pmtiles
from jotr_vegmap_to_portolan.portolan import generate_portolan

cli = typer.Typer()


@cli.command()
def main() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="jotr_vegmap_to_portolan_"))
    rprint(f"[yellow]Using tempdir: [bold]{tmpdir}[/]")

    input_data_stac_filepath = get_input_data(tmpdir=tmpdir)
    rprint(
        f"[yellow]Fetched and unzipped input data: [bold]{input_data_stac_filepath}[/]"
    )

    (tmpdir / ASSETS_DIRNAME).mkdir()
    parqueted_stac_filepath = generate_parquet(
        input_data_stac_filepath=input_data_stac_filepath,
        tmpdir=tmpdir,
    )
    rprint(f"[yellow]Generated parquet: [bold]{parqueted_stac_filepath}[/]")

    pmtiled_stac_filepath = generate_pmtiles(parqueted_stac_filepath)
    rprint(f"[yellow]Generated PMTiles: [bold]{pmtiled_stac_filepath}[/]")

    portolaned_stac_filepath = generate_portolan(pmtiled_stac_filepath)
    rprint(f"[green]Output: [bold]{portolaned_stac_filepath}[/]")

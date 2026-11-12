import tempfile
from pathlib import Path
from typing import Annotated

import typer
from rich import print as rprint

from jotr_vegmap_to_portolan.dirs import ASSETS_DIRNAME, OUTPUT_DIRNAME
from jotr_vegmap_to_portolan.download import get_input_data
from jotr_vegmap_to_portolan.parquet import generate_parquet
from jotr_vegmap_to_portolan.pmtiles import generate_pmtiles
from jotr_vegmap_to_portolan.portolan import generate_portolan

cli = typer.Typer()

# TODO: Simplify things a bit -- we're repeating a lot of logic to open catalogs. Steps
# can be expressed as a simple data structure, and transformation functions can be
# simplified to callbacks that receive and output python objects, then the caller can
# do reading and writing? ¯\_(ツ)_/¯


@cli.command()
def main(
    target_dir: Annotated[
        Path | None,
        typer.Argument(
            help=(
                "The location to output the catalog;"
                " if unspecified, will use temp directory"
            ),
        ),
    ] = None,
) -> None:
    try:
        tmpdir = Path(tempfile.mkdtemp(prefix="jotr_vegmap_to_portolan_"))
        rprint(f"[yellow]Using tempdir: [bold]{tmpdir}[/]")

        input_data_stac_filepath = get_input_data(tmpdir=tmpdir)
        rprint(
            f"[yellow]Fetched and unzipped input data:"
            f" [bold]{input_data_stac_filepath}[/]",
        )

        (tmpdir / ASSETS_DIRNAME).mkdir()
        parqueted_stac_filepath = generate_parquet(
            input_data_stac_filepath=input_data_stac_filepath,
            tmpdir=tmpdir,
        )
        rprint(f"[yellow]Generated parquet: [bold]{parqueted_stac_filepath}[/]")

        pmtiled_stac_filepath = generate_pmtiles(
            parqueted_stac_filepath=parqueted_stac_filepath,
            tmpdir=tmpdir,
        )
        rprint(f"[yellow]Generated PMTiles: [bold]{pmtiled_stac_filepath}[/]")

        portolaned_stac_filepath = generate_portolan(
            pmtiled_stac_filepath=pmtiled_stac_filepath,
            target_dir=target_dir or tmpdir / OUTPUT_DIRNAME,
        )
        rprint(f"[green]Output: [bold]{portolaned_stac_filepath}[/]")
    except Exception as e:
        rprint(f"[red]Error: [bold]{e}[/]")
        raise

import tempfile
from pathlib import Path

import typer
from rich import print as rprint

from jotr_vegmap_to_portolan.download import get_input_data
from jotr_vegmap_to_portolan.parquet import generate_parquet
from jotr_vegmap_to_portolan.pmtiles import generate_pmtiles
from jotr_vegmap_to_portolan.portolan import generate_portolan

cli = typer.Typer()


@cli.command()
def main():
    tmpdir = Path(tempfile.mkdtemp(prefix="jotr_vegmap_to_portolan_"))
    rprint(f"[green]Using tempdir: [bold]{tmpdir}[/]")

    input_data_stac = get_input_data(tmpdir=tmpdir)
    parqueted_stac = generate_parquet(input_data)
    pmtiled_stac = generate_pmtiles(parqueted)

    portolaned_stac = generate_portolan(pmtiled)

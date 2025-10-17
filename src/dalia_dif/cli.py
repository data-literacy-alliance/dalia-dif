"""Command line interface for :mod:`dalia_dif`."""

import sys
from pathlib import Path

import click

__all__ = [
    "main",
]


@click.group()
def main() -> None:
    """CLI for dalia_dif."""


@main.command()
@click.option("--dif-version", type=click.Choice(["1.3"]), default="1.3")
@click.argument("location")
def validate(location: str, dif_version: str) -> None:
    """Validate a local/remote file or local folder of DIF-encoded CSVs."""
    from dalia_dif.dif13 import read_dif13

    fail = False
    p = Path(location)
    if p.exists() and p.is_dir():
        p = p.expanduser().resolve()

        click.echo(f"validating directory: {p}")
        for path in p.glob("*.csv"):
            click.secho(f"\n> {path.relative_to(p)}", fg="green")
            errors: list[str] = []
            read_dif13(path, error_accumulator=errors)
            if errors:
                fail = True
                for error in errors:
                    click.secho(error, fg="red")
        if fail:
            click.secho("validation failed", fg="red")
            sys.exit(1)

    else:
        errors = []
        read_dif13(location, error_accumulator=errors)
        if errors:
            for error in errors:
                click.secho(error, fg="red")

            click.secho("validation failed", fg="red")
            sys.exit(1)


@main.command()
@click.argument("location", type=Path)
def lint(location: Path) -> None:
    """Lint CSV files in the curation directory."""
    import uuid

    import pandas as pd

    from .dif13.constants import DIF_HEADER_ID

    count = 0
    for path in location.glob("*.csv"):
        df = pd.read_csv(path, sep=",")
        if DIF_HEADER_ID not in df.columns:
            click.secho(f"missing column {DIF_HEADER_ID} in {path}")
            new_columns = [DIF_HEADER_ID, *df.columns]
            df[DIF_HEADER_ID] = df.index.map(lambda _: str(uuid.uuid4()))
            df = df[new_columns]
            df.to_csv(path, sep=",", index=False)
        count += len(df)
    click.echo(f"There are a total of {count:,} rows")


@main.command()
@click.option("--dif-version", type=click.Choice(["1.3"]), default="1.3")
@click.option("--format")
@click.option("-o", "--output", type=Path)
@click.argument("location")
def convert(location: str, dif_version: str, format: str | None, output: Path | None) -> None:
    """Validate a DIF file."""
    from dalia_dif.dif13 import read_dif13, write_dif13_jsonl, write_dif13_rdf

    oers = read_dif13(location)

    if output is None:
        if format == "jsonl":
            write_dif13_jsonl(oers)
        else:
            write_dif13_rdf(oers)
    elif output.suffix == ".ttl":
        write_dif13_rdf(oers, path=output, format=format)
    elif output.suffix == ".jsonl":
        write_dif13_jsonl(oers, path=output)
    else:
        click.secho(f"unhandled extension: {output.suffix}. Use .ttl or .jsonl", fg="red")


if __name__ == "__main__":
    main()

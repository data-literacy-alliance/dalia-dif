"""Command line interface for :mod:`dalia_dif`."""

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
    """Validate a DIF file."""
    from dalia_dif.dif13 import read_dif13

    read_dif13(location)


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

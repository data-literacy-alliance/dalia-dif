"""Command line interface for :mod:`dalia_dif`."""

import click

__all__ = [
    "main",
]


@click.group()
def main() -> None:
    """CLI for dalia_dif."""


@main.command()
@click.option("--dif-version", type=click.Choice(["1.3"]), default="1.3")
def validate(dif_version: str) -> None:
    """Validate a DIF file."""
    click.secho(f"DIF version: {dif_version}")


if __name__ == "__main__":
    main()

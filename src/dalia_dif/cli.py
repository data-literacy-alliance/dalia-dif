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
@click.argument("location")
def validate(location: str, dif_version: str) -> None:
    """Validate a DIF file."""
    from dalia_dif.dif13 import read_dif13

    if location.startswith("http://") or location.startswith("https://"):
        from io import StringIO

        import requests

        with requests.get(location, timeout=5) as res:
            sio = StringIO(res.text)
            sio.name = location.split("/")[-1]
            read_dif13(sio)
    else:
        read_dif13(location)


if __name__ == "__main__":
    main()

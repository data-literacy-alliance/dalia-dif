"""Command line interface for :mod:`dalia_dif`."""

import click

__all__ = [
    "main",
]


@click.command()
def main() -> None:
    """CLI for dalia_dif."""


if __name__ == "__main__":
    main()

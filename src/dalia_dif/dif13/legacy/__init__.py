"""A legacy implementation of DIF v1.3 from Frank Lange that parses direclty into RDF."""

from .learning_resource import parse_dif13_row_legacy, read_dif13

__all__ = [
    "parse_dif13_row_legacy",
    "read_dif13",
]

"""Terms from FaBiO, the FRBR-aligned Bibliographic Ontology."""

from rdflib import Namespace

__all__ = [
    "FABIO",
]
FABIO = Namespace("http://purl.org/spar/fabio/")

# Properties
# https://sparontologies.github.io/fabio/current/fabio.html#d4e205
hasDiscipline = FABIO["hasDiscipline"]
# https://sparontologies.github.io/fabio/current/fabio.html#d4e1689
hasSubtitle = FABIO["hasSubtitle"]

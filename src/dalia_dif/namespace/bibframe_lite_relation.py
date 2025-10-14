"""Terms from Bibframe Lite + Relation (http://bibfra.me/vocab/relation/)."""

from rdflib import Namespace

__all__ = [
    "BIBFRAME",
]

BIBFRAME = Namespace("http://bibfra.me/vocab/relation/")

# Properties
supportinghost = BIBFRAME["supportinghost"]

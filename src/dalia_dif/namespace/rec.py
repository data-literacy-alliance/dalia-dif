"""Terms from The Recommendation Ontology (http://purl.org/ontology/rec/core#)."""

from rdflib import Namespace

__all__ = [
    "REC",
]

REC = Namespace("http://purl.org/ontology/rec/core#")

# Properties
recommender = REC["recommender"]

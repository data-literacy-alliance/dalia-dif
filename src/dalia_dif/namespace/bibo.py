"""Terms from the Bibliographic Ontology (https://dcmi.github.io/bibo/)."""

from rdflib import Namespace

__all__ = [
    "BIBO",
]

BIBO = Namespace("http://purl.org/ontology/bibo/")

# Types
Article = BIBO["Article"]
Book = BIBO["Book"]
Report = BIBO["Report"]
Thesis = BIBO["Thesis"]
Webpage = BIBO["Webpage"]

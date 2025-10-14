"""Terms from Metadata4Ing (https://w3id.org/nfdi4ing/metadata4ing)."""

from rdflib import Namespace

__all__ = [
    "METADATA4ING",
]
METADATA4ING = Namespace("http://w3id.org/nfdi4ing/metadata4ing#")

# Properties
hasRorId = METADATA4ING["hasRorId"]
orcidId = METADATA4ING["orcidId"]

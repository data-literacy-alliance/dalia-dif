"""Terms from DataCite to DCAT-AP Mapping (https://ec-jrc.github.io/datacite-to-dcat-ap/)."""

from rdflib import Namespace

__all__ = [
    "CITEDCAT",
]
CITEDCAT = Namespace("https://w3id.org/citedcat-ap/")

# Properties
isSupplementedBy = CITEDCAT["isSupplementedBy"]
isSupplementTo = CITEDCAT["isSupplementTo"]

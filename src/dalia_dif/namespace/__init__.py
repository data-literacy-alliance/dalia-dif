"""Namespaces for DALIA DIF."""

import curies
import rdflib
from rdflib import DCTERMS, RDF, SDO, Graph, Namespace

from .bibframe_lite_relation import BIBFRAME
from .bibo import BIBO
from .citedcat import CITEDCAT
from .educor import EDUCOR
from .fabio import FABIO
from .hcrt import HCRT
from .metadata4ing import METADATA4ING
from .modalia import MODALIA
from .rec import REC

__all__ = [
    "BIBFRAME",
    "BIBO",
    "CITEDCAT",
    "CONVERTER",
    "DALIA_COMMUNITY",
    "DALIA_OER",
    "DOI",
    "EDUCOR",
    "FABIO",
    "HCRT",
    "HSFS",
    "ISO639_3",
    "METADATA4ING",
    "MODALIA",
    "NAMESPACE_PREFIXES",
    "OCCO",
    "ORCID",
    "REC",
    "ROR",
    "SPDX_LICENSE",
    "T4FS",
    "WIKIDATA",
    "YOUTUBE_PLAYLIST",
    "YOUTUBE_VIDEO",
    "ZENODO_RECORD",
    "bind",
    "get_base_graph",
]

DALIA_COMMUNITY = Namespace("https://id.dalia.education/community/")
DALIA_OER = Namespace("https://id.dalia.education/learning-resource/")
ISO639_3 = Namespace("http://lexvo.org/id/iso639-3/")
LEXVO = Namespace("http://lexvo.org/ontology#")
HSFS = Namespace("https://w3id.org/kim/hochschulfaechersystematik/")
YOUTUBE_VIDEO = Namespace("https://www.youtube.com/watch?v=")
YOUTUBE_PLAYLIST = Namespace("https://www.youtube.com/playlist?list=")
SPDX_LICENSE = Namespace("http://spdx.org/licenses/")
SPDX_TERM = Namespace("http://spdx.org/rdf/terms#")
WIKIDATA = Namespace("http://www.wikidata.org/entity/")
ZENODO_RECORD = Namespace("https://doi.org/10.5281/zenodo.")
OCCO = Namespace("http://purl.obolibrary.org/obo/OCCO_")
T4FS = Namespace("http://purl.obolibrary.org/obo/T4FS_")
ORCID = Namespace("https://orcid.org/")
ROR = Namespace("https://ror.org/")
DOI = Namespace("https://doi.org/")
OBO = Namespace("http://purl.obolibrary.org/obo/")
OBOINOWL = Namespace("http://www.geneontology.org/formats/oboInOwl#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")


NAMESPACE_PREFIXES: dict[str, Namespace] = {
    "schema": SDO._NS,
    "ror": ROR,
    "doi": DOI,
    "dcterms": DCTERMS._NS,
    "bflr": BIBFRAME,
    "rdf": RDF._NS,
    "bibo": BIBO,
    "citedcat": CITEDCAT,
    "dalia-community": DALIA_COMMUNITY,
    "dalia.oer": DALIA_OER,
    "educor": EDUCOR,
    "fabio": FABIO,
    "kim.hcrt": HCRT,
    "m4i": METADATA4ING,
    "modalia": MODALIA,
    "rec": REC,
    "iso639": ISO639_3,
    "hsfs": HSFS,
    "youtube.video": YOUTUBE_VIDEO,
    "youtube.playlist": YOUTUBE_PLAYLIST,
    "spdx.license": SPDX_LICENSE,
    "spdx": SPDX_TERM,
    "wikidata": WIKIDATA,
    "zenodo": ZENODO_RECORD,
    "occo": OCCO,
    "t4fs": T4FS,
    "oboInOwl": OBOINOWL,
    "obo": OBO,
    "skos": SKOS,
    "lexvo": LEXVO,
}

CONVERTER = curies.Converter.from_prefix_map({k: str(v) for k, v in NAMESPACE_PREFIXES.items()})


def bind(graph: rdflib.Graph) -> None:
    """Add default namespaces to a graph."""
    for curie_prefix, uri_prefix in CONVERTER.bimap.items():
        graph.bind(curie_prefix, Namespace(uri_prefix))


def get_base_graph() -> Graph:
    """Get a graph with namespaces already bound."""
    graph = Graph()
    bind(graph)
    return graph

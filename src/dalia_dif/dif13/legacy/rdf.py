"""RDF utilities for DIF v1.3."""

from functools import lru_cache

import pystow
import rdflib
from rdflib import XSD, Literal, URIRef
from rdflib.plugins.sparql import prepareQuery

__all__ = [
    "check_discipline_exists",
    "check_resource_type_exists",
    "get_discipline_graph",
    "get_language_graph",
    "get_language_uriref",
    "get_license_uriref",
    "get_licenses_graph",
    "get_resource_type_graph",
]

HOCHSCHULFAECHERSYSTEMATIK_TTL = "https://github.com/dini-ag-kim/hochschulfaechersystematik/raw/refs/tags/v2024-02-08/hochschulfaechersystematik.ttl"
HFS_EXISTS_QUERY = prepareQuery("""\
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    ASK { ?discipline a skos:Concept . }
""")


@lru_cache(1)
def get_discipline_graph() -> rdflib.Graph:
    """Get the disciplines graph from DINI-KIM's Hochschulfaechersystematik (HSFS)."""
    return pystow.ensure_rdf("dalia", url=HOCHSCHULFAECHERSYSTEMATIK_TTL)


@lru_cache
def check_discipline_exists(discipline_uriref: URIRef) -> bool:
    result = get_discipline_graph().query(
        HFS_EXISTS_QUERY,
        initBindings={"discipline": discipline_uriref},
    )
    if result.askAnswer is None:
        raise RuntimeError
    return result.askAnswer


LICENSES_TTL = (
    "https://github.com/spdx/license-list-data/raw/refs/tags/v3.25.0/rdfturtle/licenses.ttl"
)

GET_LICENSE_URI_FROM_SPDX_QUERY = prepareQuery(
    """\
    SELECT ?license
    WHERE { ?license spdx:licenseId ?identifier }
    """,
    initNs={"spdx": "http://spdx.org/rdf/terms#"},
)


@lru_cache(1)
def get_licenses_graph() -> rdflib.Graph:
    """Get a licenses graph from SPDX."""
    graph = pystow.ensure_rdf("dalia", url=LICENSES_TTL)
    graph.bind("spdx", "http://spdx.org/rdf/terms#")
    return graph


@lru_cache
def get_license_uriref(identifier: str) -> URIRef | None:
    results = get_licenses_graph().query(
        GET_LICENSE_URI_FROM_SPDX_QUERY, initBindings={"identifier": Literal(identifier)}
    )

    if not results:
        return None

    first_result = next(results.__iter__())
    return first_result.license  # type:ignore[union-attr,return-value]


LEXVO_RDF = "http://www.lexvo.org/resources/lexvo_2013-02-09.rdf.gz"
LANGUAGE_URI_QUERY = prepareQuery("""
    PREFIX lexvo: <http://lexvo.org/ontology#>

    SELECT ?language_uri
    WHERE {
        ?language_uri lexvo:iso6392BCode|lexvo:iso6392TCode|lexvo:iso639P1Code|lexvo:iso639P3PCode ?language .
    }
""")


@lru_cache(1)
def get_language_graph() -> rdflib.Graph:
    """Get the 3-letter language code graph."""
    graph = pystow.ensure_rdf("dalia", url=LEXVO_RDF, parse_kwargs={"format": "xml"})
    graph.bind("lexvo", "http://lexvo.org/ontology#")
    return graph


@lru_cache
def get_language_uriref(language: str) -> URIRef | None:
    results = get_language_graph().query(
        LANGUAGE_URI_QUERY, initBindings={"language": Literal(language, datatype=XSD.string)}
    )

    if not results:
        return None

    first_result = next(results.__iter__())
    return first_result.language_uri  # type:ignore[union-attr,return-value]


HCRT_TTL = "https://raw.githubusercontent.com/dini-ag-kim/hcrt/3fa0effce8b07ece585c1564f047cea18eec4cad/hcrt.ttl"
HCRT_TERM_EXISTS_QUERY = prepareQuery("""\
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    ASK { ?term a skos:Concept . }
""")


@lru_cache(1)
def get_resource_type_graph() -> rdflib.Graph:
    """Get the learning resource type graph from DINI-KIM's Hochschulcampus Ressourcentypen (HCRT) graph."""
    return pystow.ensure_rdf("dalia", url=HCRT_TTL)


@lru_cache
def check_resource_type_exists(hcrt_term: URIRef) -> bool:
    """Check if the resource type exists in DINI-KIM's HCRT resource."""
    result = get_resource_type_graph().query(
        HCRT_TERM_EXISTS_QUERY, initBindings={"term": hcrt_term}
    )
    if result.askAnswer is None:
        raise RuntimeError
    return result.askAnswer

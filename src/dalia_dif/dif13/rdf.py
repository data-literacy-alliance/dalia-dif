"""RDF utilities for DIF v1.3."""

from __future__ import annotations

from functools import lru_cache

import pystow
import rdflib
from rdflib import SDO, SKOS, XSD, Literal, URIRef
from rdflib.plugins.sparql import prepareQuery
from tqdm import tqdm

__all__ = [
    "add_background_triples",
    "check_discipline_exists",
    "check_resource_type_exists",
    "get_discipline_graph",
    "get_discipline_label",
    "get_language_graph",
    "get_language_uriref",
    "get_license_uriref",
    "get_licenses_graph",
    "get_modalia_graph",
    "get_resource_type_graph",
]

HOCHSCHULFAECHERSYSTEMATIK_TTL = "https://github.com/dini-ag-kim/hochschulfaechersystematik/raw/refs/tags/v2024-02-08/hochschulfaechersystematik.ttl"
HFS_EXISTS_QUERY = prepareQuery("""\
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    ASK { ?discipline a skos:Concept . }
""")
HFS_LABEL_QUERY = prepareQuery("""\
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT ?label {
        ?discipline skos:prefLabel ?label .
        FILTER(LANG(?label) = 'en') .
    }
""")


@lru_cache(1)
def get_discipline_graph() -> rdflib.Graph:
    """Get the disciplines graph from DINI-KIM's Hochschulfaechersystematik (HSFS)."""
    graph = pystow.ensure_rdf("dalia", url=HOCHSCHULFAECHERSYSTEMATIK_TTL)
    _rewire_predicate(graph, URIRef("http://schema.org/isBasedOn"), SDO.isBasedOn)
    return graph


def _rewire_predicate(graph: rdflib.Graph, old: URIRef, new: URIRef) -> None:
    # they incorrectly use http for schema.org, needs rewiring
    for s, p, o in graph.triples((None, old, None)):
        graph.remove((s, p, o))
        graph.add((s, new, o))


@lru_cache
def check_discipline_exists(discipline_uriref: URIRef) -> bool:
    """Check if the discipline exists."""
    result = get_discipline_graph().query(
        HFS_EXISTS_QUERY,
        initBindings={"discipline": discipline_uriref},
    )
    if result.askAnswer is None:
        raise RuntimeError
    return result.askAnswer


def get_discipline_label(discipline_uriref: URIRef) -> str | None:
    """Get the discipline label."""
    result = get_discipline_graph().query(
        HFS_LABEL_QUERY,
        initBindings={"discipline": discipline_uriref},
    )
    rows = list(result)
    if rows:
        return str(rows[0][0])  # type:ignore[index]
    else:
        tqdm.write(f"unable to look up name for ({type(discipline_uriref)}) {discipline_uriref}")
        return None


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
    """Get the reference for a license."""
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
""")  # noqa:E501


@lru_cache(1)
def get_language_graph() -> rdflib.Graph:
    """Get the 3-letter language code graph."""
    graph = pystow.ensure_rdf("dalia", url=LEXVO_RDF, parse_kwargs={"format": "xml"})
    graph.bind("lexvo", "http://lexvo.org/ontology#")
    _rewire_predicate(graph, URIRef("http://www.w3.org/2008/05/skos#prefLabel"), SKOS.prefLabel)
    return graph


@lru_cache
def get_language_uriref(language: str) -> URIRef | None:
    """Get a URI ref based on a language."""
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
    """Get the learning resource type graph.

    This comes from DINI-KIM's Hochschulcampus Ressourcentypen (HCRT) graph.
    """
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


MODALIA_TTL = "https://git.rwth-aachen.de/dalia/dalia-ontology/-/raw/main/MoDalia.ttl"


def get_modalia_graph(*, force: bool = False) -> rdflib.Graph:
    """Get the MoDalia graph."""
    graph = pystow.ensure_rdf("dalia", url=HCRT_TTL, force=force)
    return graph


def add_background_triples(graph: rdflib.Graph, force: bool = False) -> None:
    """Enrich graph."""
    graph += get_modalia_graph(force=force)
    graph += get_resource_type_graph()
    graph += get_language_graph()
    graph += get_licenses_graph()
    graph += get_discipline_graph()

"""Utilities for DIF v1.3."""

from __future__ import annotations

from rdflib import RDF, BNode, Graph, Node

__all__ = [
    "create_rdf_collection",
]


def create_rdf_collection(g: Graph, elements: list[Node]) -> Node | None:
    """Create an RDF collection and return the first node, or None if the list is empty."""
    # Note: RDFLib's Collection class implementation seems to be broken. Thus, we will
    # care for the low-level triple encoding of the linked list.

    if not elements:
        return None

    list_first_node = head = BNode()
    for node in elements[0:-1]:
        g.add((head, RDF.first, node))
        rest = BNode()
        g.add((head, RDF.rest, rest))
        head = rest
    g.add((head, RDF.first, elements[-1]))
    g.add((head, RDF.rest, RDF.nil))

    return list_first_node

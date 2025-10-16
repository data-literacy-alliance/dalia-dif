from rdflib import URIRef

from dalia_dif.dif13.legacy.components import add_description_to_lr
from dalia_dif.namespace import get_base_graph as graph
from tests.util import same_graphs


def test_add_description_to_lr_with_valid_input():
    g = graph()

    add_description_to_lr(
        g,
        URIRef("http://example.com/something1"),
        "  This is a very cool learning resource for research data management.     ",
    )
    add_description_to_lr(g, URIRef("http://example.com/something2"), "  ")

    expected = graph().parse(
        data="""
        @prefix dcterms: <http://purl.org/dc/terms/> .

        <http://example.com/something1> dcterms:description
            "This is a very cool learning resource for research data management." .
    """
    )

    assert same_graphs(g, expected)

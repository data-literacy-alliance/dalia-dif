from rdflib import URIRef

from dalia_dif.dif13.legacy.components import add_version_to_lr
from dalia_dif.dif13.legacy.constants import get_base_dalia_graph as graph
from tests.util import same_graphs


def test_add_version_to_lr_with_valid_input():
    g = graph()

    add_version_to_lr(g, URIRef("http://example.com/something1"), "  2.3     ")
    add_version_to_lr(g, URIRef("http://example.com/something2"), "    ")

    expected = graph().parse(
        data="""
        @prefix schema: <https://schema.org/> .

        <http://example.com/something1> schema:version "2.3" .
    """
    )

    assert same_graphs(g, expected)

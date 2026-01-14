import pytest
from rdflib import URIRef

from dalia_dif.dif13.legacy.components import add_keywords_to_lr
from dalia_dif.namespace import get_base_graph as graph
from tests.util import same_graphs


def test_add_keywords_to_lr_with_valid_input()-> None:
    g = graph()

    add_keywords_to_lr(g, URIRef("http://example.com/something1"), "    data quality     ")
    add_keywords_to_lr(
        g,
        URIRef("http://example.com/something2"),
        "  metadata    *   open educational resources   ",
    )
    add_keywords_to_lr(g, URIRef("http://example.com/something3"), "    ")

    expected = graph().parse(
        data="""
        @prefix schema: <https://schema.org/> .

        <http://example.com/something1> schema:keywords "data quality" .
        <http://example.com/something2> schema:keywords "metadata", "open educational resources" .
    """
    )

    assert same_graphs(g, expected)


@pytest.mark.parametrize(
    "keywords, expected_error_msg",
    [
        (
            "  keyword1   *    ",
            "Empty keyword",
        ),
    ],
)
def test_add_keywords_to_lr_raises_exception_on_invalid_input(keywords: str, expected_error_msg: str)-> None:
    g = graph()

    with pytest.raises(Exception, match=expected_error_msg):
        add_keywords_to_lr(g, URIRef("http://example.com/something"), keywords)

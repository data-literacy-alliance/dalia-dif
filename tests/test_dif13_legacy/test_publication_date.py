import pytest
from rdflib import URIRef

from dalia_dif.dif13.legacy.components import add_publication_date_to_lr
from dalia_dif.namespace import get_base_graph as graph
from tests.util import same_graphs


def test_publication_date_to_lr_with_valid_input():
    g = graph()

    add_publication_date_to_lr(g, URIRef("http://example.com/something1"), "   2022-04-06 ")
    add_publication_date_to_lr(g, URIRef("http://example.com/something2"), "  1995-10   ")
    add_publication_date_to_lr(g, URIRef("http://example.com/something3"), "    2042   ")
    add_publication_date_to_lr(g, URIRef("http://example.com/something4"), "  12.12.1991  ")
    add_publication_date_to_lr(g, URIRef("http://example.com/something5"), " 11.1992  ")
    add_publication_date_to_lr(g, URIRef("http://example.com/something6"), "  ")

    expected = graph().parse(
        data="""
        @prefix schema: <https://schema.org/> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        <http://example.com/something1> schema:datePublished "2022-04-06"^^xsd:date .
        <http://example.com/something2> schema:datePublished "1995-10"^^xsd:gYearMonth .
        <http://example.com/something3> schema:datePublished "2042"^^xsd:gYear .
        <http://example.com/something4> schema:datePublished "1991-12-12"^^xsd:date .
        <http://example.com/something5> schema:datePublished "1992-11"^^xsd:gYearMonth .
    """
    )

    assert same_graphs(g, expected)


@pytest.mark.parametrize(
    "publication_date, expected_error_msg",
    [
        ("  abcdef  ", 'Invalid publication date "abcdef"'),
        (" 2050-13 ", 'Invalid publication date "2050-13"'),
        (" 2050-12-32 ", 'Invalid publication date "2050-12-32"'),
        (" 13.2050 ", 'Invalid publication date "13.2050"'),
        (" 32.12.2050 ", 'Invalid publication date "32.12.2050"'),
        # TODO add back validation
        # ("2022-02-29", "day is out of range for month"),
        # ("2020-11-31", "day is out of range for month"),
        # ("29.02.2001", "day is out of range for month"),
        # ("31.09.2000", "day is out of range for month"),
    ],
)
def test_add_publication_date_to_lr_raises_exception_on_invalid_input(
    publication_date, expected_error_msg
):
    g = graph()

    with pytest.raises(Exception, match=expected_error_msg):
        add_publication_date_to_lr(g, URIRef("http://example.com/something"), publication_date)

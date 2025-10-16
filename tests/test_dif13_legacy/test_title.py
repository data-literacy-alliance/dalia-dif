import pytest
from rdflib import URIRef

from dalia_dif.dif13.legacy.components import add_title_to_lr
from dalia_dif.namespace import get_base_graph as graph
from tests.util import same_graphs


def test_add_title_to_lr_with_example_from_dif():
    g = graph()

    add_title_to_lr(
        g,
        URIRef("http://example.com/something1"),
        "   cool learning resource   :   with a cool subtitle ",
    )
    add_title_to_lr(g, URIRef("http://example.com/something2"), "   a title without subtitle")
    add_title_to_lr(
        g, URIRef("http://example.com/something3"), "   a title with an empty subtitle:         "
    )

    expected = graph().parse(
        data="""
        @prefix dcterms: <http://purl.org/dc/terms/> .
        @prefix fabio: <http://purl.org/spar/fabio/> .

        <http://example.com/something1> dcterms:title "cool learning resource" ;
            fabio:hasSubtitle "with a cool subtitle" .
        <http://example.com/something2> dcterms:title "a title without subtitle" .
        <http://example.com/something3> dcterms:title "a title with an empty subtitle:" .
    """
    )

    assert same_graphs(g, expected)


@pytest.mark.parametrize(
    "title, expected_error_msg",
    [
        (
            "    ",
            "Empty Title field",
        ),
    ],
)
def test_add_title_to_lr_raises_exception_on_invalid_input(title, expected_error_msg):
    g = graph()

    with pytest.raises(Exception, match=expected_error_msg):
        add_title_to_lr(g, URIRef("http://example.com/something"), title)

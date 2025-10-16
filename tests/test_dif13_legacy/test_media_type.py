import pytest
from rdflib import URIRef

from dalia_dif.dif13.legacy.components import add_media_types_to_lr
from dalia_dif.namespace import get_base_graph as graph
from tests.util import same_graphs


def test_add_media_types_to_lr_with_valid_input():
    g = graph()

    add_media_types_to_lr(
        g, URIRef("http://example.com/something1"), "    text   *    Presentation     "
    )
    add_media_types_to_lr(g, URIRef("http://example.com/something2"), "  VIDEO   ")
    add_media_types_to_lr(g, URIRef("http://example.com/something3"), "    ")

    expected = graph().parse(
        data="""
        @prefix mo: <https://purl.org/ontology/modalia#> .
        @prefix schema: <https://schema.org/> .

        <http://example.com/something1> mo:hasMediaType schema:Text, schema:PresentationDigitalDocument .
        <http://example.com/something2> mo:hasMediaType schema:VideoObject .
    """
    )

    assert same_graphs(g, expected)


@pytest.mark.parametrize(
    "media_types, expected_error_msg",
    [
        (
            "  text   *    ",
            "Empty media type",
        ),
        (
            "does not exist",
            'Unknown media type "does not exist"',
        ),
    ],
)
def test_add_media_types_to_lr_raises_exception_on_invalid_input(media_types, expected_error_msg):
    g = graph()

    with pytest.raises(Exception, match=expected_error_msg):
        add_media_types_to_lr(g, URIRef("http://example.com/something"), media_types)

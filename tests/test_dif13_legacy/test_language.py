import pytest
from rdflib import URIRef

from dalia_dif.dif13.legacy.components import add_languages_to_lr
from dalia_dif.namespace import get_base_graph as graph
from tests.util import same_graphs


def test_add_languages_to_lr_with_valid_input():
    g = graph()

    add_languages_to_lr(g, URIRef("http://example.com/something1"), "    de     ")
    add_languages_to_lr(g, URIRef("http://example.com/something2"), "  en     *     de    * tlh ")
    add_languages_to_lr(g, URIRef("http://example.com/something3"), "    ")

    expected = graph().parse(
        data="""
        @prefix dcterms: <http://purl.org/dc/terms/> .

        <http://example.com/something1> dcterms:language <http://lexvo.org/id/iso639-3/deu> .
        <http://example.com/something2> dcterms:language <http://lexvo.org/id/iso639-3/deu> ,
            <http://lexvo.org/id/iso639-3/eng> , <http://lexvo.org/id/iso639-3/tlh> .
    """
    )

    assert same_graphs(g, expected)


@pytest.mark.parametrize(
    "languages, expected_error_msg",
    [
        (
            "  de   *    ",
            "Empty language",
        ),
        (
            "does not exist",
            'Invalid language identifier "does not exist". Please check Lexvo.',
        ),
    ],
)
def test_add_languages_to_lr_raises_exception_on_invalid_input(languages, expected_error_msg):
    g = graph()

    with pytest.raises(Exception, match=expected_error_msg):
        add_languages_to_lr(g, URIRef("http://example.com/something"), languages)

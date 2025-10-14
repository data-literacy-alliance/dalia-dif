import pytest
from rdflib import URIRef

from dalia_dif.dif13.legacy.components import add_disciplines_to_lr
from dalia_dif.dif13.legacy.constants import get_base_dalia_graph as graph
from tests.util import same_graphs


def test_add_disciplines_to_lr_with_valid_input():
    g = graph()

    add_disciplines_to_lr(
        g,
        URIRef("http://example.com/something1"),
        " https://w3id.org/kim/hochschulfaechersystematik/n079  ",
    )
    add_disciplines_to_lr(
        g,
        URIRef("http://example.com/something2"),
        "https://w3id.org/kim/hochschulfaechersystematik/n0",
    )
    add_disciplines_to_lr(
        g,
        URIRef("http://example.com/something3"),
        "  https://w3id.org/kim/hochschulfaechersystematik/n42  *   https://w3id.org/kim/hochschulfaechersystematik/n22",
    )
    with pytest.raises(ValueError):
        add_disciplines_to_lr(
            g,
            URIRef("http://example.com/something4"),
            "does not exist in the Hochschulfaechersystematik",
        )
    add_disciplines_to_lr(g, URIRef("http://example.com/something5"), "   ")

    expected = graph().parse(
        data="""
        @prefix fabio: <http://purl.org/spar/fabio/> .

        <http://example.com/something1> fabio:hasDiscipline <https://w3id.org/kim/hochschulfaechersystematik/n079> .
        <http://example.com/something2> fabio:hasDiscipline <https://w3id.org/kim/hochschulfaechersystematik/n0> .
        <http://example.com/something3> fabio:hasDiscipline <https://w3id.org/kim/hochschulfaechersystematik/n22>,
            <https://w3id.org/kim/hochschulfaechersystematik/n42> .
    """
    )

    assert same_graphs(g, expected)


@pytest.mark.parametrize(
    "disciplines, expected_error_msg",
    [
        (
            "  *  ",
            "Empty discipline",
        ),
        # (
        #     "https://w3id.org/kim/hochschulfaechersystematik/n0 * https://w3id.org/kim/hochschulfaechersystematik/1234",
        #     'Discipline "https://w3id.org/kim/hochschulfaechersystematik/1234" '
        #     'does not exist in the Hochschulfaechersystematik',
        # ),
    ],
)
def test_add_disciplines_to_lr_raises_exception_on_invalid_input(disciplines, expected_error_msg):
    g = graph()

    with pytest.raises(Exception, match=expected_error_msg):
        add_disciplines_to_lr(g, URIRef("http://example.com/something"), disciplines)

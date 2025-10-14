import pytest
from rdflib import URIRef

from dalia_dif.dif13.legacy.components import add_links_to_lr
from dalia_dif.dif13.legacy.constants import get_base_dalia_graph as graph
from tests.util import same_graphs


def test_add_links_to_lr_with_examples_from_dif():
    g = graph()

    add_links_to_lr(
        g,
        URIRef("http://example.com/something1"),
        "     https://doi.org/10.5281/zenodo.10122153    ",
    )
    add_links_to_lr(
        g,
        URIRef("http://example.com/something2"),
        "https://data-affairs.affective-societies.de/lerneinheiten/forschungsethik-und-datenethik/",
    )
    add_links_to_lr(
        g,
        URIRef("http://example.com/something3"),
        "    https://doi.org/10.25656/01:29235    *     https://doi.org/10.5281/zenodo.10828758  ",
    )

    expected = graph().parse(
        data="""
        @prefix schema: <https://schema.org/> .

        <http://example.com/something1> schema:url <https://doi.org/10.5281/zenodo.10122153> .
        <http://example.com/something2> schema:url
            <https://data-affairs.affective-societies.de/lerneinheiten/forschungsethik-und-datenethik/> .
        <http://example.com/something3> schema:url <https://doi.org/10.25656/01:29235>,
            <https://doi.org/10.5281/zenodo.10828758> .
    """
    )

    assert same_graphs(g, expected)


@pytest.mark.parametrize(
    "links, expected_error_msg",
    [
        (
            "    ",
            "Empty Link field",
        ),
        (
            "  *  ",
            "Empty link",
        ),
    ],
)
def test_add_links_to_lr_raises_exception_on_invalid_input(links, expected_error_msg):
    g = graph()

    with pytest.raises(Exception, match=expected_error_msg):
        add_links_to_lr(g, URIRef("http://example.com/something"), links)

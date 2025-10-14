import pytest
from rdflib import URIRef

from dalia_dif.dif13.legacy.components import add_proficiency_levels_to_lr
from dalia_dif.dif13.legacy.constants import get_base_dalia_graph as graph
from tests.util import same_graphs


def test_add_proficiency_levels_to_lr_with_valid_input():
    g = graph()

    add_proficiency_levels_to_lr(
        g, URIRef("http://example.com/something1"), "    novice   *    advanced beginner     "
    )
    add_proficiency_levels_to_lr(g, URIRef("http://example.com/something2"), "    ")

    expected = graph().parse(
        data="""
        @prefix mo: <https://purl.org/ontology/modalia#> .

        <http://example.com/something1> mo:requiresProficiencyLevel mo:Beginner, mo:Novice .
    """
    )

    assert same_graphs(g, expected)


@pytest.mark.parametrize(
    "proficiency_levels, expected_error_msg",
    [
        (
            "  advanced beginner   *    ",
            "Empty proficiency level",
        ),
        (
            "does not exist",
            'Unknown proficiency level "does not exist"',
        ),
    ],
)
def test_add_proficiency_levels_to_lr_raises_exception_on_invalid_input(
    proficiency_levels, expected_error_msg
):
    g = graph()

    with pytest.raises(Exception, match=expected_error_msg):
        add_proficiency_levels_to_lr(g, URIRef("http://example.com/something"), proficiency_levels)

import pytest
from rdflib import URIRef

from dalia_dif.dif13.legacy.components import add_target_groups_to_lr
from dalia_dif.namespace import get_base_graph as graph
from tests.util import same_graphs


def test_add_target_groups_to_lr_with_valid_input() -> None:
    g = graph()

    add_target_groups_to_lr(
        g, URIRef("http://example.com/something1"), "    student (BA)    *   student (MA)     "
    )
    add_target_groups_to_lr(
        g, URIRef("http://example.com/something2"), "  student (PhD) * data steward   * researcher"
    )
    add_target_groups_to_lr(g, URIRef("http://example.com/something3"), "    ")

    expected = graph().parse(
        data="""
        @prefix mo: <https://purl.org/ontology/modalia#> .

        <http://example.com/something1> mo:hasTargetGroup mo:BachelorStudent, mo:MastersStudent .
        <http://example.com/something2> mo:hasTargetGroup mo:PhDStudent, mo:DataSteward, mo:Researcher .
    """
    )

    assert same_graphs(g, expected)


@pytest.mark.parametrize(
    "target_groups, expected_error_msg",
    [
        (
            "  data steward   *    ",
            "Empty target group",
        ),
        (
            "does not exist",
            'Unknown target group "does not exist"',
        ),
    ],
)
def test_add_target_groups_to_lr_raises_exception_on_invalid_input(
    target_groups: str, expected_error_msg: str
) -> None:
    g = graph()

    with pytest.raises(Exception, match=expected_error_msg):
        add_target_groups_to_lr(g, URIRef("http://example.com/something"), target_groups)

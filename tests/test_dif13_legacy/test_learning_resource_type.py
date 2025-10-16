import pytest
from rdflib import URIRef

from dalia_dif.dif13.legacy.components import (
    MEDIA_TYPE_EXCEPTIONS,
    add_learning_resource_types_to_lr,
)
from dalia_dif.namespace import get_base_graph as graph
from tests.util import same_graphs


def test_add_learning_resource_types_to_lr_with_valid_input():
    g = graph()

    add_learning_resource_types_to_lr(
        g, URIRef("http://example.com/something1"), "    lecture     "
    )
    add_learning_resource_types_to_lr(
        g,
        URIRef("http://example.com/something2"),
        "  CodeNotebook    *    TUTORIAL  *  bibo:Thesis  ",
    )
    add_learning_resource_types_to_lr(
        g,
        URIRef("http://example.com/something3"),
        "    https://w3id.org/kim/hcrt/course   * https://w3id.org/kim/hcrt/drill_and_practice   * article * Tutorial  ",
    )

    with pytest.raises(ValueError):
        add_learning_resource_types_to_lr(
            g,
            URIRef("http://example.com/something4"),
            "  does not exist  *   https://w3id.org/kim/hcrt/does_not_exist  ",
        )
    add_learning_resource_types_to_lr(g, URIRef("http://example.com/something5"), "    ")

    assert [] == add_learning_resource_types_to_lr(
        g, URIRef("http://example.com/something6"), " * ".join(MEDIA_TYPE_EXCEPTIONS)
    )

    expected = graph().parse(
        data="""
        @prefix bibo: <http://purl.org/ontology/bibo/> .
        @prefix hcrt: <https://w3id.org/kim/hcrt/> .
        @prefix mo: <https://purl.org/ontology/modalia#> .

        <http://example.com/something1> mo:hasLearningType mo:Lecture .
        <http://example.com/something2> mo:hasLearningType mo:CodeNotebook, mo:Tutorial, bibo:Thesis .
        <http://example.com/something3> mo:hasLearningType bibo:Article, mo:Tutorial, hcrt:course,
            hcrt:drill_and_practice .
    """
    )

    assert same_graphs(g, expected)


@pytest.mark.parametrize(
    "learning_resource_types, expected_error_msg",
    [
        (
            "  Lecture   *    ",
            "Empty learning resource type",
        ),
        # (
        #     "does not exist",
        #     'Unknown learning resource type "does not exist"',
        # ),
        # (
        #     "https://w3id.org/kim/hcrt/does_not_exist",
        #     'Unknown learning resource type "https://w3id.org/kim/hcrt/does_not_exist"',
        # ),
    ],
)
def test_add_learning_resource_types_to_lr_raises_exception_on_invalid_input(
    learning_resource_types, expected_error_msg
):
    g = graph()

    with pytest.raises(Exception, match=expected_error_msg):
        add_learning_resource_types_to_lr(
            g, URIRef("http://example.com/something"), learning_resource_types
        )

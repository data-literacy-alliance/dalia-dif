import pytest
from rdflib import URIRef

from dalia_dif.dif13.legacy.components import add_related_works_to_lr
from dalia_dif.namespace import get_base_graph as graph
from tests.util import same_graphs


def test_add_related_works_to_lr_with_valid_input():
    g = graph()

    add_related_works_to_lr(
        g,
        URIRef("http://example.com/something1"),
        "   isBasedOn:https://doi.org/10.5281/zenodo.8297723     ",
    )
    add_related_works_to_lr(
        g,
        URIRef("http://example.com/something2"),
        "  isSupplementTo:https://doi.org/10.5281/zenodo.10122153  ",
    )
    add_related_works_to_lr(
        g,
        URIRef("http://example.com/something3"),
        "  wasRevisionOf:https://doi.org/10.5281/zenodo.8297723   *  hasPart:https://doi.org/10.5281/zenodo.10122153",
    )
    add_related_works_to_lr(g, URIRef("http://example.com/something4"), "    ")

    expected = graph().parse(
        data="""
        @prefix citedcat: <https://w3id.org/citedcat-ap/> .
        @prefix mo: <https://purl.org/ontology/modalia#> .
        @prefix prov: <http://www.w3.org/ns/prov#> .
        @prefix schema: <https://schema.org/> .

        <http://example.com/something1> mo:isBasedOn <https://doi.org/10.5281/zenodo.8297723> .
        <http://example.com/something2> citedcat:isSupplementTo <https://doi.org/10.5281/zenodo.10122153> .
        <http://example.com/something3> prov:wasRevisionOf <https://doi.org/10.5281/zenodo.8297723> ;
            schema:hasPart <https://doi.org/10.5281/zenodo.10122153> .
    """
    )

    assert same_graphs(g, expected)


@pytest.mark.parametrize(
    "related_works, expected_error_msg",
    [
        (
            "  isBasedOn:https://doi.org/10.5281/zenodo.8297723   *    ",
            "Empty related work",
        ),
        (
            "does not exist:https://doi.org/10.5281/zenodo.8297723",
            'Unknown related work relation "does not exist"',
        ),
        (
            "    isBasedOn:     ",
            'Link missing in related work "isBasedOn:"',
        ),
        (
            "    isBasedOn     ",
            'Link missing in related work "isBasedOn"',
        ),
    ],
)
def test_add_related_works_to_lr_raises_exception_on_invalid_input(
    related_works, expected_error_msg
):
    g = graph()

    with pytest.raises(Exception, match=expected_error_msg):
        add_related_works_to_lr(g, URIRef("http://example.com/something"), related_works)

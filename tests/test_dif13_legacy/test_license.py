import pytest
from rdflib import URIRef

from dalia_dif.dif13.legacy.components import add_license_to_lr
from dalia_dif.namespace import get_base_graph as graph
from tests.util import same_graphs


def test_add_license_to_lr_with_valid_license_identifiers():
    g = graph()

    add_license_to_lr(g, URIRef("http://example.com/something1"), " CC-BY-4.0  ")
    add_license_to_lr(g, URIRef("http://example.com/something2"), "Apache-2.0")
    add_license_to_lr(g, URIRef("http://example.com/something3"), "     CC-BY-SA-3.0-DE")
    add_license_to_lr(g, URIRef("http://example.com/something4"), "  proprietary  ")

    expected = graph().parse(
        data="""
        @prefix dcterms: <http://purl.org/dc/terms/> .
        @prefix mo: <https://purl.org/ontology/modalia#> .

        <http://example.com/something1> dcterms:license <http://spdx.org/licenses/CC-BY-4.0> .
        <http://example.com/something2> dcterms:license <http://spdx.org/licenses/Apache-2.0> .
        <http://example.com/something3> dcterms:license <http://spdx.org/licenses/CC-BY-SA-3.0-DE> .
        <http://example.com/something4> dcterms:license mo:ProprietaryLicense .
    """
    )

    assert same_graphs(g, expected)


@pytest.mark.parametrize(
    "license, expected_error_msg",
    [
        (
            "    ",
            "Empty License field",
        ),
        (
            "  Does not exist ",
            'Invalid license identifier "Does not exist"',
        ),
    ],
)
def test_add_license_to_lr_raises_exception_on_invalid_input(license, expected_error_msg):
    g = graph()

    with pytest.raises(Exception, match=expected_error_msg):
        add_license_to_lr(g, URIRef("http://example.com/something"), license)

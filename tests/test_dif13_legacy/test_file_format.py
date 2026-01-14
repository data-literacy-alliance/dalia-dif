import pytest
from rdflib import URIRef

from dalia_dif.dif13.legacy.components import add_file_formats_to_lr
from dalia_dif.namespace import get_base_graph as graph
from tests.util import same_graphs


def test_add_file_formats_to_lr_with_valid_input()-> None:
    g = graph()

    add_file_formats_to_lr(g, URIRef("http://example.com/something1"), "   .pptx  ")
    add_file_formats_to_lr(g, URIRef("http://example.com/something2"), "  .pdf    *   .odt  ")
    add_file_formats_to_lr(g, URIRef("http://example.com/something3"), "  pdf    *   odt  ")
    add_file_formats_to_lr(g, URIRef("http://example.com/something4"), "    ")

    expected = graph().parse(
        data="""
        @prefix dcterms: <http://purl.org/dc/terms/> .

        <http://example.com/something1> dcterms:format "PPTX" .
        <http://example.com/something2> dcterms:format "ODT", "PDF" .
        <http://example.com/something3> dcterms:format "ODT", "PDF" .
    """
    )

    assert same_graphs(g, expected)


@pytest.mark.parametrize(
    "file_formats, expected_error_msg",
    [
        (
            "     * .abc  ",
            "Empty file format",
        ),
        (
            "   .a bc    ",
            'Could not match regex for file format ".a bc"',
        ),
    ],
)
def test_add_file_formats_to_lr_raises_exception_on_invalid_input(file_formats: str, expected_error_msg: str)-> None:
    g = graph()

    with pytest.raises(Exception, match=expected_error_msg):
        add_file_formats_to_lr(g, URIRef("http://example.com/something"), file_formats)

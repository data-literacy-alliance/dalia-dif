import pytest
from rdflib import URIRef

from dalia_dif.dif13.legacy.components import add_size_to_lr
from dalia_dif.dif13.legacy.constants import get_base_dalia_graph as graph
from tests.util import same_graphs


def test_add_size_to_lr_with_valid_input():
    g = graph()

    add_size_to_lr(g, URIRef("http://example.com/something1"), "   3.14     ")
    add_size_to_lr(g, URIRef("http://example.com/something2"), "    ")

    expected = graph().parse(
        data="""
        @prefix schema: <https://schema.org/> .

        <http://example.com/something1> schema:fileSize "3.14 MB" .
    """
    )

    assert same_graphs(g, expected)


# just invalid instead
@pytest.mark.parametrize(
    "size, expected_error_msg",
    [
        (
            "  invalid size   ",
            "could not convert string to float: 'invalid'",
        ),
        (
            "  3,14  ",
            "could not convert string to float: '3,14'",
        ),
    ],
)
def test_add_size_to_lr_raises_exception_on_invalid_input(size, expected_error_msg):
    g = graph()

    with pytest.raises(Exception, match=expected_error_msg):
        add_size_to_lr(g, URIRef("http://example.com/something"), size)

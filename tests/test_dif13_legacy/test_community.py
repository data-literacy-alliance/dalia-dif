import pytest
from rdflib import URIRef

from dalia_dif.dif13.legacy.components import add_communities_to_lr
from dalia_dif.namespace import get_base_graph as graph
from tests.util import same_graphs


def test_add_communities_to_lr_with_valid_input():
    g = graph()

    add_communities_to_lr(
        g,
        URIRef("http://example.com/something1"),
        "   NFDI4Culture    (S)    *   NFDI4Chem   (R)  ",
    )
    add_communities_to_lr(
        g,
        URIRef("http://example.com/something2"),
        "     Nationale Forschungsdateninfrastruktur (NFDI)    (SR)    ",
    )
    with pytest.raises(ValueError):
        add_communities_to_lr(g, URIRef("http://example.com/something3"), "   does not exist (R)  ")
    add_communities_to_lr(g, URIRef("http://example.com/something4"), "     ")

    expected = graph().parse(
        data="""
        @prefix bflr: <http://bibfra.me/vocab/relation/> .
        @prefix dalia-community: <https://id.dalia.education/community/> .
        @prefix rec: <http://purl.org/ontology/rec/core#> .

        <http://example.com/something1> bflr:supportinghost dalia-community:6a21dd4a-200c-44e3-85b8-68fb31d510af ;
            rec:recommender dalia-community:bead62a8-c3c2-46d6-9eb1-ffeaba38d5bf .
        <http://example.com/something2> bflr:supportinghost dalia-community:3dc37495-59bb-4505-851f-e09c5df8e356 ;
            rec:recommender dalia-community:3dc37495-59bb-4505-851f-e09c5df8e356 .
    """
    )

    assert same_graphs(g, expected)


@pytest.mark.parametrize(
    "communities, expected_error_msg",
    [
        (
            "   NFDI4Culture (S)   *   ",
            "Empty community",
        ),
        (
            "  NFDI4Culture (R)  *  NFDI4Chem   ",
            '\\[line:0\\] Community was incorrectly encoded "NFDI4Chem". Did you remember to include one of \\(S\\), \\(R\\), \\(SR\\), or \\(RS\\) at the end?',
        ),
        # (
        #     "  NFDI4Culture (S)  *  does not exist     (R)   ",
        #     'Unknown community "does not exist"',
        # ),
    ],
)
def test_add_communities_to_lr_raises_exception_on_invalid_input(communities, expected_error_msg):
    g = graph()

    with pytest.raises(Exception, match=expected_error_msg):
        add_communities_to_lr(g, URIRef("http://example.com/something"), communities)

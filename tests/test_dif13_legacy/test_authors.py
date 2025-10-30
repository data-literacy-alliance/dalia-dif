import pytest
from rdflib import URIRef

from dalia_dif.dif13.legacy.authors import add_authors_to_lr
from dalia_dif.namespace import get_base_graph as graph
from tests.util import same_graphs


def test_add_authors_to_lr_with_no_authors() -> None:
    g = graph()
    lr_node = URIRef("http://example.com/something")

    add_authors_to_lr(g, lr_node, "  *    *  ", row_number=1)

    assert same_graphs(g, graph())


def test_add_authors_to_lr_with_examples_from_dif() -> None:
    g = graph()

    add_authors_to_lr(
        g,
        URIRef("http://example.com/something1"),
        "   Mustermann   ,   Max    : {   https://orcid.org/0000-0001-2345-6789  }   *   Musterfrau , Paula  ",
        row_number=1,
    )
    add_authors_to_lr(
        g,
        URIRef("http://example.com/something2"),
        "Müllermeier, John * Musterkollegin, Alex * "
        "Nationale Forschungsdateninfrastruktur   : {organization    https://ror.org/05qj6w324    }",
        row_number=1,
    )
    add_authors_to_lr(
        g,
        URIRef("http://example.com/something3"),
        "NFDI4Chem   : {organization   http://www.wikidata.org/entity/Q96678459   } * "
        "Example-Organization-without-identifier : {organization    }",
        row_number=1,
    )
    add_authors_to_lr(g, URIRef("http://example.com/something4"), "  n/a   ", row_number=1)

    expected = graph().parse(
        data="""
        @prefix m4i: <http://w3id.org/nfdi4ing/metadata4ing#> .
        @prefix owl: <http://www.w3.org/2002/07/owl#> .
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix schema: <https://schema.org/> .

        <http://example.com/something1> schema:author (
            [
                a schema:Person ;
                schema:familyName "Mustermann" ;
                schema:givenName "Max" ;
                m4i:orcidId "https://orcid.org/0000-0001-2345-6789"
            ]
            [
                a schema:Person ;
                schema:familyName "Musterfrau" ;
                schema:givenName "Paula"
            ]
        ) ;
        <https://dalia.education/authorUnordered> [
            a schema:Person ;
            schema:familyName "Mustermann" ;
            schema:givenName "Max" ;
            m4i:orcidId "https://orcid.org/0000-0001-2345-6789"
        ] ,
        [
            a schema:Person ;
            schema:familyName "Musterfrau" ;
            schema:givenName "Paula"
        ] .

        <http://example.com/something2> schema:author (
            [
                a schema:Person ;
                schema:familyName "Müllermeier" ;
                schema:givenName "John"
            ]
            [
                a schema:Person ;
                schema:familyName "Musterkollegin" ;
                schema:givenName "Alex"
            ]
            [
                a schema:Organization ;
                schema:name "Nationale Forschungsdateninfrastruktur" ;
                m4i:hasRorId "https://ror.org/05qj6w324"
            ]
        ) ;
        <https://dalia.education/authorUnordered> [
            a schema:Person ;
            schema:familyName "Müllermeier" ;
            schema:givenName "John"
        ] ,
        [
            a schema:Person ;
            schema:familyName "Musterkollegin" ;
            schema:givenName "Alex"
        ] ,
        [
            a schema:Organization ;
            schema:name "Nationale Forschungsdateninfrastruktur" ;
            m4i:hasRorId "https://ror.org/05qj6w324"
        ] .

        <http://example.com/something3> schema:author (
            [
                a schema:Organization ;
                schema:name "NFDI4Chem" ;
                owl:sameAs <http://www.wikidata.org/entity/Q96678459>
            ]
            [
                a schema:Organization ;
                schema:name "Example-Organization-without-identifier"
            ]
        ) ;
        <https://dalia.education/authorUnordered> [
            a schema:Organization ;
            schema:name "NFDI4Chem" ;
            owl:sameAs <http://www.wikidata.org/entity/Q96678459>
        ] ,
        [
            a schema:Organization ;
            schema:name "Example-Organization-without-identifier"
        ] .
    """
    )

    assert same_graphs(g, expected)


@pytest.mark.parametrize(
    "authors, expected_error_msg",
    [
        (
            "   ",
            "Empty Authors field",
        ),
        (
            "ACME : {organization https://ror.org/12345}",
            'Invalid identifier in "ACME : {organization https://ror.org/12345}": https://ror.org/12345',
        ),
        (
            "Person : {https://orcid.org/1234}",
            'Invalid identifier in "Person : {https://orcid.org/1234}": https://orcid.org/1234',
        ),
        (
            "ABC, Mr. : {https://orcid.org/1234}\n ACME : {organization http://www.wikidata.org/entity/Q288523}",
            'Could not match regex for organization "ABC, Mr. : {https://orcid.org/1234}\n'
            ' ACME : {organization http://www.wikidata.org/entity/Q288523}"',
        ),
    ],
)
def test_add_authors_to_lr_raises_exception_on_invalid_input(
    authors: str, expected_error_msg: str
) -> None:
    g = graph()

    with pytest.raises(Exception, match=expected_error_msg):
        add_authors_to_lr(g, URIRef("http://example.com/something"), authors, row_number=1)

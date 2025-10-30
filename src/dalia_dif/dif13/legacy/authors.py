"""A legacy implementation of author parsing DIF v1.3 from Frank Lange."""

import re
from pathlib import Path

import base32_crockford
from rdflib import RDF, Graph
from rdflib.term import BNode, Literal, Node, URIRef

from ..constants import DIF_SEPARATOR
from ..predicates import (
    AUTHOR_PREDICATE,
    AUTHOR_UNORDERED_PREDICATE,
    ORGANIZATION_CLASS,
    ORGANIZATION_NAME_PREDICATE,
    ORGANIZATION_ROR_PREDICATE,
    ORGANIZATION_WIKIDATA_PREDICATE,
    PERSON_CLASS,
    PERSON_FAMILY_NAME_PREDICATE,
    PERSON_GIVEN_NAME_PREDICATE,
    PERSON_ORCID_PREDICATE,
)
from ..utils import create_rdf_collection

#: part of this regex is from https://ror.readme.io/docs/identifier
ROR_RE = re.compile(r"^https://ror\.org/0[a-hj-km-np-tv-z|0-9]{6}\d{2}$")
ORCID_RE = re.compile(r"^https?://orcid\.org/\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")
WIKIDATA_RE = re.compile(r"^http://www\.wikidata\.org/entity/Q\d*$")


def _create_organization_author(
    g: Graph, organization: str, row_number: int, path: Path | None = None
) -> Node:
    match = re.search(r"^(?P<name>.+)\s:\s{organization\s?(?P<identifier>.*)}$", organization)

    if not match:
        raise Exception(f'Could not match regex for organization "{organization}"')

    organization_name = match.group("name").strip()
    organization_identifier = match.group("identifier")

    organization_node = BNode()
    g.add((organization_node, RDF.type, ORGANIZATION_CLASS))
    g.add((organization_node, ORGANIZATION_NAME_PREDICATE, Literal(organization_name)))

    if organization_identifier and (organization_identifier := organization_identifier.strip()):
        if is_valid_ror_id(organization_identifier):
            g.add((organization_node, ORGANIZATION_ROR_PREDICATE, Literal(organization_identifier)))
        elif is_valid_wikidata_concept_uri(organization_identifier):
            g.add(
                (
                    organization_node,
                    ORGANIZATION_WIKIDATA_PREDICATE,
                    URIRef(organization_identifier),
                )
            )
        else:
            raise Exception(
                f'[{path} {row_number}] Invalid identifier in "{organization}": {organization_identifier}'
            )

    return organization_node


def _create_person_author(g: Graph, person: str, row_number: int, path: Path | None = None) -> Node:
    person_substrings = person.split(" : ")
    name_substrings = person_substrings[0].split(",")

    person_node = BNode()
    g.add((person_node, RDF.type, PERSON_CLASS))
    g.add((person_node, PERSON_FAMILY_NAME_PREDICATE, Literal(name_substrings[0].strip())))

    if len(name_substrings) > 1:
        g.add((person_node, PERSON_GIVEN_NAME_PREDICATE, Literal(name_substrings[1].strip())))

    if (len(person_substrings) > 1) and (
        match := re.match(r"^{(?P<identifier>.*)}$", person_substrings[1])
    ):
        person_identifier = match.group("identifier").strip()
        if is_valid_orcid(person_identifier):
            g.add((person_node, PERSON_ORCID_PREDICATE, Literal(person_identifier)))
        else:
            raise Exception(
                f'[{path} {row_number}] Invalid identifier in "{person}": {person_identifier}'
            )

    return person_node


def _create_author(g: Graph, author: str, row_number: int, path: Path | None = None) -> Node | None:
    if not author:
        return None

    if re.search(r"\s*:\s*{organization.*}", author):
        return _create_organization_author(g, author, row_number=row_number, path=path)
    return _create_person_author(g, author, row_number=row_number, path=path)


def _add_ordered_list_of_authors_to_lr(
    g: Graph, lr_node: Node, authors: str, row_number: int, path: Path | None = None
) -> None:
    author_nodes = []
    for author in authors.split(DIF_SEPARATOR):
        if author_node := _create_author(g, author.strip(), row_number=row_number, path=path):
            author_nodes.append(author_node)

    if authors_list := create_rdf_collection(g, author_nodes):
        g.add((lr_node, AUTHOR_PREDICATE, authors_list))


def _add_unordered_set_of_authors_to_lr(
    g: Graph, lr_node: Node, authors: str, row_number: int, path: Path | None = None
) -> None:
    for author in authors.split(DIF_SEPARATOR):
        if author_node := _create_author(g, author.strip(), row_number=row_number, path=path):
            g.add((lr_node, AUTHOR_UNORDERED_PREDICATE, author_node))


def add_authors_to_lr(
    g: Graph, lr_node: Node, authors: str, row_number: int, path: Path | None = None
) -> None:
    if not authors.strip():
        raise Exception("Empty Authors field")

    if authors.strip().lower() == "n/a":
        return None

    _add_ordered_list_of_authors_to_lr(g, lr_node, authors, row_number=row_number, path=path)
    _add_unordered_set_of_authors_to_lr(g, lr_node, authors, row_number=row_number, path=path)
    return None


# see https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier#2-checksum
def _generate_check_digit(base_digits: str) -> str:
    total = 0
    for c in base_digits:
        digit = int(c)
        total = (total + digit) * 2
    remainder = total % 11
    result = (12 - remainder) % 11
    return "X" if result == 10 else str(result)


def _check_orcid_checksum(orcid: str) -> bool:
    digits = orcid.split("/")[-1].replace("-", "")
    return _generate_check_digit(digits[:-1]) == digits[-1]


def is_valid_orcid(orcid: str) -> bool:
    """Check if an ORCID string is syntactically correct. Does not check for existence of the ORCID."""
    return bool(ORCID_RE.search(orcid)) and _check_orcid_checksum(orcid)


def _check_ror_id_checksum(ror_id: str) -> bool:
    # inverse of https://github.com/ror-community/ror-api/blob/034592be42654ad6638103e2a7638cab344d2880/rorapi/management/commands/generaterorid.py#L6
    record = ror_id.split("/")[-1]
    checksum = record[-2:]
    n_encoded = record[0:-2]
    n = base32_crockford.decode(n_encoded)

    return checksum == str(98 - ((n * 100) % 97)).zfill(2)


def is_valid_ror_id(ror_id: str) -> bool:
    """Check if a ROR ID is syntactically correct. Does not check for existence of the ROR ID."""
    return bool(ROR_RE.search(ror_id)) and _check_ror_id_checksum(ror_id)


def is_valid_wikidata_concept_uri(concept_uri: str) -> bool:
    """Check if a Wikidata concept URI is syntactically correct.

    Does not check for existence of the Wikidata Entity behind this URI.
    """
    return bool(WIKIDATA_RE.search(concept_uri))

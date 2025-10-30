"""A concrete implementation of the DALIA Interchange Format (DIF) v1.3."""

from __future__ import annotations

import datetime
from typing import Annotated, ClassVar

import rdflib
from pydantic import UUID4, Field
from pydantic_extra_types.language_code import ISO639_3
from pydantic_metamodel.api import (
    Addable,
    IsPredicateObject,
    PredicateAnnotation,
    PredicateObject,
    RDFInstanceBaseModel,
    RDFResource,
    WithPredicate,
    WithPredicateNamespace,
    Year,
)
from rdflib import BNode, Node, URIRef

from . import constants
from .predicates import (
    AUTHOR_PREDICATE,
    AUTHOR_UNORDERED_PREDICATE,
    DATE_PUBLISHED_PREDICATE,
    DESCRIPTION_PREDICATE,
    DISCIPLINE_PREDICATE,
    EDUCATIONAL_RESOURCE_CLASS,
    FILE_FORMAT_PREDICATE,
    FILE_SIZE_PREDICATE,
    KEYWORDS_PREDICATE,
    LANGUAGE_PREDICATE,
    LEARNING_RESOURCE_TYPE_PREDICATE,
    LICENSE_PREDICATE,
    LINK_PREDICATE,
    MEDIA_TYPES_PREDICATE,
    ORGANIZATION_CLASS,
    ORGANIZATION_NAME_PREDICATE,
    ORGANIZATION_ROR_PREDICATE,
    ORGANIZATION_WIKIDATA_PREDICATE,
    PERSON_CLASS,
    PERSON_FAMILY_NAME_PREDICATE,
    PERSON_GIVEN_NAME_PREDICATE,
    PERSON_ORCID_PREDICATE,
    PROFICIENCY_LEVEL_PREDICATE,
    RECOMMENDING_COMMUNITY_PRED,
    SUBTITLE_PREDICATE,
    SUPPORTING_COMMUNITY_PRED,
    TARGET_GROUP_PREDICATE,
    TITLE_PREDICATE,
    VERSION_PREDICATE,
    XREF_PREDICATE,
)
from .utils import create_rdf_collection
from ..namespace import DALIA_OER, WIKIDATA
from ..namespace import ISO639_3 as ISO639_3_NS

__all__ = [
    "AuthorDIF13",
    "EducationalResourceDIF13",
    "OrganizationDIF13",
]


class AuthorDIF13(RDFInstanceBaseModel):
    """Represents an author in DIF v1.3."""

    rdf_type: ClassVar[URIRef] = PERSON_CLASS

    family_name: Annotated[str, WithPredicate(PERSON_FAMILY_NAME_PREDICATE)]
    given_name: Annotated[str, WithPredicate(PERSON_GIVEN_NAME_PREDICATE)]
    orcid: Annotated[str | None, WithPredicate(PERSON_ORCID_PREDICATE)] = None

    @property
    def name(self) -> str:
        """Get the full name."""
        return f"{self.given_name} {self.family_name}"

    def get_node(self) -> Node:
        """Get a blank node for the author."""
        return BNode()


class OrganizationDIF13(RDFInstanceBaseModel):
    """Represents an organization in DIF v1.3."""

    rdf_type: ClassVar[URIRef] = ORGANIZATION_CLASS

    name: Annotated[str, WithPredicate(ORGANIZATION_NAME_PREDICATE)]
    ror: Annotated[str | None, WithPredicate(ORGANIZATION_ROR_PREDICATE)] = None
    wikidata: Annotated[
        str | None, WithPredicateNamespace(ORGANIZATION_WIKIDATA_PREDICATE, WIKIDATA)
    ] = None

    def get_node(self) -> Node:
        """Get a blank node for the organization."""
        return BNode()


class AuthorAnnotation(PredicateAnnotation):
    """A custom annotation for serializing the author list."""

    def add_to_graph(self, graph: rdflib.Graph, node: Node, value: Addable) -> None:
        """Add to the graph."""
        if not isinstance(value, list):
            raise TypeError

        # the type ignores are fine because we know we're an AddableBase
        author_nodes = [self._handle_object(graph, s) for s in value]  # type:ignore[arg-type]
        if authors_list := create_rdf_collection(graph, author_nodes):
            graph.add((node, AUTHOR_PREDICATE, authors_list))

        # do this a second time to assign new blank nodes
        # (yes this is dumb, but it's for backwards compatibility)
        author_nodes = [self._handle_object(graph, s) for s in value]  # type:ignore[arg-type]
        for author in author_nodes:
            graph.add((node, AUTHOR_UNORDERED_PREDICATE, author))


class EducationalResourceDIF13(RDFInstanceBaseModel):
    """Represents an educational resource in DIF v1.3."""

    rdf_type: ClassVar[URIRef] = EDUCATIONAL_RESOURCE_CLASS

    uuid: UUID4
    title: Annotated[str, WithPredicate(TITLE_PREDICATE)] = Field(
        ..., description=constants.DIF_HEADER_TITLE.__doc__
    )
    subtitle: Annotated[str | None, WithPredicate(SUBTITLE_PREDICATE)] = None
    authors: Annotated[list[AuthorDIF13 | OrganizationDIF13], AuthorAnnotation()] = Field(
        default_factory=list, description=constants.DIF_HEADER_AUTHORS.__doc__, min_length=1
    )
    license: Annotated[RDFResource | None, WithPredicate(LICENSE_PREDICATE)] = Field(
        None, description=constants.DIF_HEADER_LICENSE.__doc__
    )
    links: Annotated[list[RDFResource], WithPredicate(LINK_PREDICATE)] = Field(
        default_factory=list, description=constants.DIF_HEADER_LINK.__doc__
    )
    supporting_communities: Annotated[
        list[RDFResource], WithPredicate(SUPPORTING_COMMUNITY_PRED)
    ] = Field(default_factory=list, description=constants.DIF_HEADER_COMMUNITY.__doc__)
    recommending_communities: Annotated[
        list[RDFResource], WithPredicate(RECOMMENDING_COMMUNITY_PRED)
    ] = Field(default_factory=list, description=constants.DIF_HEADER_COMMUNITY.__doc__)
    description: Annotated[str | None, WithPredicate(DESCRIPTION_PREDICATE)] = Field(
        None, description=constants.DIF_HEADER_DESCRIPTION.__doc__
    )
    disciplines: Annotated[list[RDFResource] | None, WithPredicate(DISCIPLINE_PREDICATE)] = Field(
        default_factory=list, description=constants.DIF_HEADER_DISCIPLINE.__doc__
    )
    file_formats: Annotated[list[str] | None, WithPredicate(FILE_FORMAT_PREDICATE)] = Field(
        default_factory=list
    )
    keywords: Annotated[list[str], WithPredicate(KEYWORDS_PREDICATE)] = Field(default_factory=list)
    xrefs: Annotated[list[RDFResource], WithPredicate(XREF_PREDICATE)] = Field(default_factory=list)
    languages: Annotated[
        list[ISO639_3], WithPredicateNamespace(LANGUAGE_PREDICATE, ISO639_3_NS)
    ] = Field(default_factory=list)
    learning_resource_types: Annotated[
        list[RDFResource] | None, WithPredicate(LEARNING_RESOURCE_TYPE_PREDICATE)
    ] = Field(default_factory=list)
    media_types: Annotated[list[RDFResource], WithPredicate(MEDIA_TYPES_PREDICATE)] = Field(
        default_factory=list
    )
    proficiency_levels: Annotated[list[RDFResource], WithPredicate(PROFICIENCY_LEVEL_PREDICATE)] = (
        Field(default_factory=list)
    )
    publication_date: Annotated[
        Year | datetime.date | datetime.datetime | None, WithPredicate(DATE_PUBLISHED_PREDICATE)
    ] = None
    target_groups: Annotated[list[RDFResource] | None, WithPredicate(TARGET_GROUP_PREDICATE)] = (
        Field(default_factory=list)
    )
    related_works: Annotated[list[PredicateObject[RDFResource]], IsPredicateObject()] = Field(
        default_factory=list
    )
    file_size: Annotated[str | None, WithPredicate(FILE_SIZE_PREDICATE)] = None
    version: Annotated[str | None, WithPredicate(VERSION_PREDICATE)] = None

    def get_node(self) -> URIRef:
        """Get the learning resource URI."""
        return DALIA_OER[str(self.uuid)]

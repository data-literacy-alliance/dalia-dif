"""Predicates for DIF v1.3."""

from __future__ import annotations

from rdflib import DCTERMS, OWL, SDO, URIRef

from ..namespace import (
    EDUCOR,
    FABIO,
    OBOINOWL,
    bibframe_lite_relation,
    citedcat,
    fabio,
    metadata4ing,
    modalia,
    rec,
)

EDUCATIONAL_RESOURCE_CLASS = EDUCOR["EducationalResource"]
ORGANIZATION_CLASS = SDO.Organization
PERSON_CLASS = SDO.Person

DISCIPLINE_PREDICATE = FABIO["hasDiscipline"]
SUPPORTING_COMMUNITY_PRED = bibframe_lite_relation.supportinghost
RECOMMENDING_COMMUNITY_PRED = rec.recommender

MEDIA_TYPES_PREDICATE = modalia.hasMediaType
PROFICIENCY_LEVEL_PREDICATE = modalia.requiresProficiencyLevel
FILE_SIZE_PREDICATE = SDO.fileSize
TARGET_GROUP_PREDICATE = modalia.hasTargetGroup
TITLE_PREDICATE = DCTERMS.title
LINK_PREDICATE = SDO.url
VERSION_PREDICATE = SDO.version
SUBTITLE_PREDICATE = fabio.hasSubtitle
LICENSE_PREDICATE = DCTERMS.license
LANGUAGE_PREDICATE = DCTERMS.language
DATE_PUBLISHED_PREDICATE = SDO.datePublished
LEARNING_RESOURCE_TYPE_PREDICATE = modalia.hasLearningType
KEYWORDS_PREDICATE = SDO.keywords
XREF_PREDICATE = OBOINOWL["hasDbXref"]
FILE_FORMAT_PREDICATE = DCTERMS.format
DESCRIPTION_PREDICATE = DCTERMS.description

AUTHOR_PREDICATE = SDO.author
AUTHOR_UNORDERED_PREDICATE = URIRef("https://dalia.education/authorUnordered")

ORGANIZATION_NAME_PREDICATE = SDO.name
ORGANIZATION_WIKIDATA_PREDICATE = OWL.sameAs
ORGANIZATION_ROR_PREDICATE = metadata4ing.hasRorId

PERSON_FAMILY_NAME_PREDICATE = SDO.familyName
PERSON_GIVEN_NAME_PREDICATE = SDO.givenName
PERSON_ORCID_PREDICATE = metadata4ing.orcidId

IS_SUPPLEMENTED_BY_PREDICATE = citedcat.isSupplementedBy
NEW_VERSION_OF_PREDICATE = modalia.isNewVersionOf

"""Constants for DIF v1.3."""

from rdflib import Graph

from ...namespace import bind

#
# Headers in DIF
#
DIF_HEADER_ID = "DALIA_ID"
DIF_HEADER_AUTHORS = "Authors"
DIF_HEADER_LICENSE = "License"
DIF_HEADER_LINK = "Link"
DIF_HEADER_TITLE = "Title"
DIF_HEADER_COMMUNITY = "Community"
DIF_HEADER_DESCRIPTION = "Description"
DIF_HEADER_DISCIPLINE = "Discipline"
DIF_HEADER_FILE_FORMAT = "FileFormat"
DIF_HEADER_KEYWORDS = "Keywords"
DIF_HEADER_LANGUAGE = "Language"
DIF_HEADER_LEARNING_RESOURCE_TYPE = "LearningResourceType"
DIF_HEADER_MEDIA_TYPE = "MediaType"
DIF_HEADER_PROFICIENCY_LEVEL = "ProficiencyLevel"
DIF_HEADER_PUBLICATION_DATE = "PublicationDate"
DIF_HEADER_TARGET_GROUP = "TargetGroup"
DIF_HEADER_RELATED_WORK = "RelatedWork"
DIF_HEADER_SIZE = "Size"
DIF_HEADER_VERSION = "Version"

#: separator used for list fields
DIF_SEPARATOR = " * "


def get_base_dalia_graph() -> Graph:
    """Get a graph with namespaces already bound."""
    graph = Graph()
    bind(graph)
    return graph

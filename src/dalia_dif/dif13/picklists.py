"""Picklists for DIF v1.3."""

from __future__ import annotations

from rdflib import PROV, SDO, URIRef

from .predicates import (
    IS_SUPPLEMENTED_BY_PREDICATE,
    NEW_VERSION_OF_PREDICATE,
    RECOMMENDING_COMMUNITY_PRED,
    SUPPORTING_COMMUNITY_PRED,
)
from ..namespace import bibo, citedcat, hcrt, modalia

__all__ = [
    "COMMUNITY_RELATIONS",
    "LEARNING_RESOURCE_TYPES",
    "MEDIA_TYPES",
    "PROFICIENCY_LEVELS",
    "PROPRIETARY_LICENSE",
    "RELATED_WORKS_RELATIONS",
    "TARGET_GROUPS",
]

TARGET_GROUPS = {
    "student (school)": modalia.StudentSchool,
    "student (ba)": modalia.BachelorStudent,
    "student (ma)": modalia.MastersStudent,
    "student (phd)": modalia.PhDStudent,
    "data steward": modalia.DataSteward,
    "teacher (school)": modalia.TeacherSchool,
    "teacher (higher education)": modalia.TeacherHighEducation,
    "researcher": modalia.Researcher,
    "content provider": modalia.ContentProvider,
}
MEDIA_TYPES = {
    "audio": SDO.AudioObject,
    "video": SDO.VideoObject,
    "text": SDO.Text,
    "presentation": SDO.PresentationDigitalDocument,
    "code": modalia.Code,  # FIXME why not SDO.SoftwareSourceCode
    "image": SDO.ImageObject,
    "multipart": modalia.Multipart,
}

PROFICIENCY_LEVELS = {
    "novice": modalia.Novice,
    "advanced beginner": modalia.Beginner,
    "competent": modalia.Competent,
    "proficient": modalia.Proficient,
    "expert": modalia.Expert,
}
PROFICIENCY_TO_ORDER: dict[URIRef, int] = {
    modalia.Novice: 0,
    modalia.Beginner: 1,
    modalia.Competent: 2,
    modalia.Proficient: 3,
    modalia.Expert: 4,
}

RELATED_WORKS_RELATIONS = {
    "isPartOf": modalia.isPartOf,
    "hasPart": SDO.hasPart,
    "isBasedOn": modalia.isBasedOn,
    "isNewerVersionOf": NEW_VERSION_OF_PREDICATE,
    "isSupplementOf": citedcat.isSupplementTo,
    "isSupplementTo": citedcat.isSupplementTo,
    "isSupplementedBy": IS_SUPPLEMENTED_BY_PREDICATE,
    "wasRevisionOf": PROV.wasRevisionOf,
    "isDuplicateOf": modalia.isDuplicateOf,
    "isTranslationOf": modalia.isTranslationOf,
}

# Entries that will be ignored during the mapping because they shall be used as media type.
# Format: URI -> media type to be used instead
MEDIA_TYPE_EXCEPTIONS = {
    hcrt.audio: "audio",
    hcrt.image: "image",
    hcrt.slide: "presentation",
    hcrt.text: "text",
    hcrt.video: "video",
}

LEARNING_RESOURCE_TYPES: dict[str, URIRef] = {
    "educational game": hcrt.educational_game,
    "case study": hcrt.case_study,
    "experiment": hcrt.experiment,
    "diagram": hcrt.diagram,
    "course": hcrt.course,
    "hcrt:diagram": hcrt.diagram,
    "hcrt:educational_game": hcrt.educational_game,
    "hcrt:case_study": hcrt.case_study,
    "hcrt:experiment": hcrt.experiment,
    # SDO
    "podcastseries": SDO.PodcastSeries,
    "schema:podcastseries": SDO.PodcastSeries,
    "code": SDO.SoftwareSourceCode,
    # BIBO
    "article": bibo.Article,
    "book": bibo.Book,
    "report": bibo.Report,
    "webpage": bibo.Webpage,
    "thesis": bibo.Thesis,
    "bibo:article": bibo.Article,
    "bibo:book": bibo.Book,
    "bibo:report": bibo.Report,
    "bibo:webpage": bibo.Webpage,
    "bibo:thesis": bibo.Thesis,
    # Internal
    "poster": modalia.Poster,
    "lecture": modalia.Lecture,
    "tutorial": modalia.Tutorial,
    "codenotebook": modalia.CodeNotebook,
    "bestpractices": modalia.BestPractices,
    "cookbook": modalia.Cookbook,
    "mo:poster": modalia.Poster,
    "mo:lecture": modalia.Lecture,
    "mo:tutorial": modalia.Tutorial,
    "mo:codenotebook": modalia.CodeNotebook,
    "mo:best-practices": modalia.BestPractices,
    "mo:cookbook": modalia.Cookbook,
    # added by charlie to clean up errors
    "interview": modalia.Interview,
    # Mappings provided by Petra and Abdel for MVP1
    # "Video": None,
    # "Presentation": None,
    # "Website": bibo.Webpage,
    # "Case studies and tutorials": hcrt.case_study,
    # "Video (Serie)": None,
    # "Conference proceeding": None,
    # "free self-paced course": None,
    # "Blogpost": None,
    # "Conference paper": bibo.Article,
    # "Figure": hcrt.diagram,
    # "Git repository": None,
    # "Jupyter Notebook": modalia.JupyterNotebook,
    # "Project deliverable": bibo.Report,
    # "Project milestone": bibo.Report,
    # "Proposal": None,
    # "Working paper": bibo.Article,
    # "Best practices and guidelines": modalia.BestPractices,
    # "Curriculum": None,
    # "Guide": None,
    # "Handbook": bibo.Book,
    # "Image": None,
    # "in person workshop": modalia.Workshop,
    # "Journal article": bibo.Article,
    # "Lesson (Self-Study Unit)": None,
    # "Other": None,
    # "Preprint": bibo.Article,
    # "School": None,
    # "Software": None,
    # "Workflow": None,
    # "Youtube Channel": None,
}

COMMUNITY_RELATIONS = {
    "S": SUPPORTING_COMMUNITY_PRED,
    "R": RECOMMENDING_COMMUNITY_PRED,
}

PROPRIETARY_LICENSE = modalia.ProprietaryLicense

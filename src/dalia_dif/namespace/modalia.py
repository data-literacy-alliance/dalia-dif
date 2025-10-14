"""Terms from the MoDalia ontology (https://git.rwth-aachen.de/dalia/dalia-ontology/-/blob/main/MoDalia.ttl)."""

from rdflib.namespace import Namespace

__all__ = [
    "MODALIA",
]

MODALIA = Namespace("https://purl.org/ontology/modalia#")

# Properties
hasLearningType = MODALIA["hasLearningType"]
hasMediaType = MODALIA["hasMediaType"]
hasTargetGroup = MODALIA["hasTargetGroup"]
isBasedOn = MODALIA["isBasedOn"]
isDuplicateOf = MODALIA["isDuplicateOf"]
isNewVersionOf = MODALIA["isNewVersionOf"]
isPartOf = MODALIA["isPartOf"]
isTranslationOf = MODALIA["isTranslationOf"]
requiresProficiencyLevel = MODALIA["requiresProficiencyLevel"]

# Types
BachelorStudent = MODALIA["BachelorStudent"]
BestPractices = MODALIA["BestPractices"]
Code = MODALIA["Code"]
CodeNotebook = MODALIA["CodeNotebook"]
ContentProvider = MODALIA["ContentProvider"]
Cookbook = MODALIA["Cookbook"]
DataSteward = MODALIA["DataSteward"]
Lecture = MODALIA["Lecture"]
MastersStudent = MODALIA["MastersStudent"]
Multipart = MODALIA["Multipart"]
PhDStudent = MODALIA["PhDStudent"]
Poster = MODALIA["Poster"]
Researcher = MODALIA["Researcher"]
StudentSchool = MODALIA["StudentSchool"]
TeacherHighEducation = MODALIA["TeacherHighEducation"]
TeacherSchool = MODALIA["TeacherSchool"]
Tutorial = MODALIA["Tutorial"]
Interview = MODALIA["Interview"]  # TODO review
Course = MODALIA["Interview"]  # TODO review

# Individuals
Beginner = MODALIA["Beginner"]
Competent = MODALIA["Competent"]
Expert = MODALIA["Expert"]
Novice = MODALIA["Novice"]
Proficient = MODALIA["Proficient"]
ProprietaryLicense = MODALIA["ProprietaryLicense"]

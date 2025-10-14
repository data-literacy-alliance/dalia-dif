"""Terms from EduCOR (https://github.com/tibonto/educor/blob/main/educor.ttl)."""

from rdflib import Namespace

__all__ = [
    "EDUCOR",
]
EDUCOR = Namespace("https://github.com/tibonto/educor#")

# Types
EducationalResource = EDUCOR["EducationalResource"]

"""Terms from Hochschulcampus Ressourcentypen (https://skohub.io/dini-ag-kim/hcrt/heads/master/w3id.org/kim/hcrt/scheme.html)."""

from rdflib import Namespace

__all__ = [
    "HCRT",
]
HCRT = Namespace("https://w3id.org/kim/hcrt/")

# Types
audio = HCRT["audio"]
case_study = HCRT["case_study"]
diagram = HCRT["diagram"]
educational_game = HCRT["educational_game"]
experiment = HCRT["experiment"]
image = HCRT["image"]
slide = HCRT["slide"]
text = HCRT["text"]
video = HCRT["video"]
course = HCRT["course"]

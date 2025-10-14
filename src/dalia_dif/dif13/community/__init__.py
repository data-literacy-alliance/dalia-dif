"""Code for curated DALIA communities."""

import csv
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent.resolve()
COMMUNITIES_PATH = HERE / "dalia_communities.csv"


def _read_mapping() -> dict[str, str]:
    rv = {}
    with open(COMMUNITIES_PATH, newline="") as csvfile:
        for row in csv.DictReader(csvfile):
            rv[row["Title"]] = row["ID"]
            for synonym in row["Synonyms"].split("|"):
                rv[synonym] = row["ID"]
    return rv


LOOKUP_DICT_COMMUNITIES = _read_mapping()

del _read_mapping

MISSING_COMMUNITIES: Counter[str] = Counter()

"""Code for curated DALIA communities."""

import csv
from collections import Counter
from pathlib import Path
from typing import Any, TypeAlias

from pydantic import UUID4, AnyHttpUrl, BaseModel, Field

HERE = Path(__file__).parent.resolve()
COMMUNITIES_PATH = HERE / "dalia_communities.csv"


class Community(BaseModel):
    """A data model for communities."""

    uuid: UUID4
    title: str
    ror: str | None = None
    website: AnyHttpUrl | None = None
    synonyms: list[str] = Field(default_factory=list)


def _process(row: dict[str, Any]) -> Community:
    if synonyms_raw := row.pop("Synonyms"):
        row["Synonyms"] = [s.strip() for s in synonyms_raw.split("|")]
    return Community.model_validate(row)


def read_communities(path: Path) -> list[Community]:
    """Read communities."""
    with open(path, newline="") as csvfile:
        return [_process(row) for row in csv.DictReader(csvfile)]


CommunityDict: TypeAlias = dict[str, str]


def get_communities_dict(path: Path) -> CommunityDict:
    rv = {}
    for community in read_communities(path):
        rv[community.title] = str(community.uuid)
        for synonym in community.synonyms:
            rv[synonym] = str(community.uuid)
    return rv


def _read_mapping() -> dict[str, str]:
    rv = {}
    for community in read_communities(COMMUNITIES_PATH):
        rv[community.title] = str(community.uuid)
        for synonym in community.synonyms:
            rv[synonym] = str(community.uuid)
    return rv


LOOKUP_DICT_COMMUNITIES: CommunityDict = get_communities_dict(COMMUNITIES_PATH)

MISSING_COMMUNITIES: Counter[str] = Counter()


def get_community_labels() -> dict[str, str]:
    """Get community labels."""
    return {
        str(community.uuid): COMMUNITY_RELABELS.get(community.title, community.title)
        for community in read_communities(COMMUNITIES_PATH)
    }


COMMUNITY_RELABELS = {
    "Nationale Forschungsdateninfrastruktur (NFDI)": "NFDI",
    "HeFDI - Hessische Forschungsdateninfrastrukturen": "HeFDI",
}

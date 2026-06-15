"""Code for curated DALIA communities."""

from collections import Counter
from pathlib import Path
from typing import Any, TypeAlias

from pydantic import UUID4, AnyHttpUrl, BaseModel, Field
from pystow.utils import safe_open_dict_reader

HERE = Path(__file__).parent.resolve()


class Community(BaseModel):
    """A data model for communities."""

    uuid: UUID4
    title: str
    ror: str | None = None
    website: AnyHttpUrl | None = None
    synonyms: list[str] = Field(default_factory=list)


RENAMES = {
    "ID": "uuid",
    "ROR": "ror",
    "Website": "website",
    "Synonyms": "synonyms",
    "Title": "title",
}


def _process(row: dict[str, Any]) -> Community:
    row = {RENAMES[k]: v for k, v in row.items() if v}
    if synonyms_raw := row.pop("synonyms", None):
        row["synonyms"] = [s.strip() for s in synonyms_raw.split("|")]
    return Community.model_validate(row)


def read_communities(path: str | Path) -> list[Community]:
    """Read communities."""
    with safe_open_dict_reader(path) as reader:
        return [_process(row) for row in reader]


CommunityDict: TypeAlias = dict[str, str]


def get_communities_dict(path: str | Path) -> CommunityDict:
    """Get a mapping from names/synonyms to UUID strings."""
    rv = {}
    for community in read_communities(path):
        rv[community.title] = str(community.uuid)
        for synonym in community.synonyms:
            rv[synonym] = str(community.uuid)
    return rv


MISSING_COMMUNITIES: Counter[str] = Counter()

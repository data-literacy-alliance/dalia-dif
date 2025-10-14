"""Reader for DIF v1.3."""

import re
from collections import Counter
from pathlib import Path

from pydantic_extra_types.language_code import ISO639_3
from pydantic_metamodel.api import PredicateObject, RDFResource, Year
from pystow.utils import safe_open_dict_reader
from rdflib import URIRef
from tqdm import tqdm

from .community import LOOKUP_DICT_COMMUNITIES
from .model import (
    AuthorDIF13,
    EducationalResourceDIF13,
    OrganizationDIF13,
)
from .picklists import (
    LOOKUP_DICT_LEARNING_RESOURCE_TYPE,
    LOOKUP_DICT_MEDIA_TYPE,
    LOOKUP_DICT_PROFICIENCY_LEVEL,
    LOOKUP_DICT_RELATED_WORKS,
    LOOKUP_DICT_TARGET_GROUP,
    PROPRIETARY_LICENSE,
)
from ..namespace import DALIA_COMMUNITY, SPDX_LICENSE
from ..utils import cleanup_languages

__all__ = [
    "parse_dif13_row",
    "read_dif13",
]

DELIMITER = " * "

ORCID_RE = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}(\d|X)$")

ORCID_URI_PREFIX = "https://orcid.org/"
ROR_URI_PREFIX = "https://ror.org/"
WIKIDATA_URI_PREFIX = "http://www.wikidata.org/entity/"
COMMUNITY_RELATION_RE = re.compile(r"^(?P<name>.*)\s\((?P<relation>S|R|SR|RS)\)$")

#: Keep track of fields in DIF CSV files that haven't
#: been explicitly processed
UNPROCESSED: Counter[str] = Counter()


def read_dif13(path: str | Path) -> list[EducationalResourceDIF13]:
    """Parse DALIA records."""
    path = Path(path).expanduser().resolve()
    with safe_open_dict_reader(path, delimiter=",") as reader:
        return [
            oer
            for idx, record in enumerate(reader, start=2)
            if (oer := parse_dif13_row(path, idx, record)) is not None
        ]


def parse_dif13_row(
    path: Path, idx: int, row: dict[str, str], *, future: bool = False
) -> EducationalResourceDIF13 | None:
    """Convert a row in a DALIA curation file to a resource, or return none if unable."""
    supporting_communities, recommending_communities = _process_communities(path, idx, row)

    external_uris = _split(row.pop("Link"))
    if future and (n4c_id := row.pop("N4C_ID", None)):
        external_uris.append(n4c_id)

    title, _, subtitle = map(str.strip, row.pop("Title").partition(":"))

    try:
        rv = EducationalResourceDIF13(
            uuid=row.pop("DALIA_ID"),
            title=title,
            subtitle=subtitle,
            authors=_process_authors(path, idx, row),
            license=_process_license(row),
            links=external_uris,
            supporting_communities=supporting_communities,
            recommending_communities=recommending_communities,
            description=row.pop("Description").strip(),
            disciplines=_process_disciplines(path, idx, row),
            file_formats=_process_formats(row),
            keywords=_split(row.pop("Keywords")),
            languages=_process_languages(row),
            learning_resource_types=_process_learning_resource_types(path, idx, row),
            media_types=_process_media_types(path, idx, row),
            proficiency_levels=_process_proficiency_levels(row),
            publication_date=_process_publication_date(row),
            target_groups=_process_target_groups(path, idx, row),
            related_works=_process_related_works(path, idx, row),
            file_size=_process_size(row),
            version=row.pop("Version") or None,
        )
    except ValueError as e:
        _log(path, idx, str(e))
        raise
    for k, v in row.items():
        if v and v.strip():
            UNPROCESSED[k] += 1
    return rv


def _split(s: str) -> list[str]:
    return [y for x in s.split(DELIMITER) if (y := x.strip())]


def _log(path: Path, line: int, text: str) -> None:
    tqdm.write(f"[{path.name} line:{line}] {text}")


def _process_publication_date(row: dict[str, str]) -> Year | str | None:
    date: str | None = row.pop("PublicationDate", None)
    if not date:
        return None
    try:
        year = int(date)
    except ValueError:
        return date
    else:
        return Year(year)


def _process_disciplines(path: Path, idx: int, row: dict[str, str]) -> list[URIRef]:
    rv = []
    for f in _split(row.pop("Discipline")):
        if f.startswith("https://w3id.org/kim/hochschulfaechersystematik/"):
            rv.append(URIRef(f))
        else:
            raise ValueError(f"invalid discipline: {f}")
    return rv


def _process_formats(row: dict[str, str]) -> list[str]:
    return [f.lstrip(".").upper() for f in _split(row.pop("FileFormat"))]


def _process_languages(row: dict[str, str]) -> list[ISO639_3]:
    return cleanup_languages(_split(row.pop("Language")))


def _process_proficiency_levels(row: dict[str, str]) -> list[URIRef]:
    return [LOOKUP_DICT_PROFICIENCY_LEVEL[x.lower()] for x in _split(row.pop("ProficiencyLevel"))]


def _process_authors(
    path: Path, idx: int, row: dict[str, str]
) -> list[AuthorDIF13 | OrganizationDIF13]:
    return [
        author
        for s in _split(row.pop("Authors"))
        if (author := _process_author(path, idx, s)) is not None
    ]


def _process_author(path: Path, idx: int, s: str) -> AuthorDIF13 | OrganizationDIF13 | None:
    if not s or s.lower() == "n/a":
        return None

    if "{" not in s:
        # assume whole thing is a name
        family_name, _, given_name = (x.strip() for x in s.rpartition(","))
        return AuthorDIF13(given_name=given_name, family_name=family_name)

    name, _, ids = s.partition(" : ")
    url = ids.lstrip("{").rstrip("}")
    if url.startswith("organization"):
        url = url.removeprefix("organization").strip()
        if url.startswith(WIKIDATA_URI_PREFIX):
            return OrganizationDIF13(name=name, wikidata=url.removeprefix(WIKIDATA_URI_PREFIX))
        elif url.startswith(ROR_URI_PREFIX):
            return OrganizationDIF13(name=name, ror=url)
        elif not url:
            return OrganizationDIF13(name=name)
        else:
            pass
    elif url.startswith(ORCID_URI_PREFIX):
        orcid = url.removeprefix(ORCID_URI_PREFIX)
        if not ORCID_RE.fullmatch(orcid):
            raise ValueError(f"path:{path} row:{idx} failed: {s}")
        family_name, _, given_name = (x.strip() for x in name.rpartition(","))
        return AuthorDIF13(
            given_name=given_name, family_name=family_name, orcid=ORCID_URI_PREFIX + orcid
        )
    elif url.startswith(ROR_URI_PREFIX):
        return OrganizationDIF13(name=name, ror=url.removeprefix(ROR_URI_PREFIX))

    _log(path, idx, f"failed to parse author list: {s}")
    return None


def _process_license(row: dict[str, str]) -> str | URIRef | None:
    identifier = row.pop("License").strip()
    if identifier == "proprietary":
        return PROPRIETARY_LICENSE
    return SPDX_LICENSE[identifier]


def _process_target_groups(path: Path, line: int, row: dict[str, str]) -> list[URIRef]:
    rv = []
    for g in _split(row.pop("TargetGroup")):
        if g.lower() in LOOKUP_DICT_TARGET_GROUP:
            rv.append(LOOKUP_DICT_TARGET_GROUP[g.lower()])
        else:
            _log(path, line, f"unable to lookup target group: {g}")
    return rv


def _process_size(row: dict[str, str]) -> str | None:
    size = row.pop("Size")
    if not size:
        return None
    if size.endswith(" MB"):
        # FIXME should not be like this
        return size
    return f"{size} MB"


def _process_learning_resource_types(path: Path, line: int, row: dict[str, str]) -> list[URIRef]:
    rv = []
    for x in _split(row.pop("LearningResourceType")):
        x = x.lower()
        if x.startswith("https://w3id.org/kim/hcrt/"):
            rv.append(URIRef(x))
        elif x in LOOKUP_DICT_LEARNING_RESOURCE_TYPE:
            rv.append(LOOKUP_DICT_LEARNING_RESOURCE_TYPE[x])
        else:
            _log(path, line, f"unable to lookup learning resource type: {x}")
    return rv


def _process_media_types(path: Path, line: int, row: dict[str, str]) -> list[URIRef]:
    rv = []
    for g in _split(row.pop("MediaType")):
        if g in LOOKUP_DICT_MEDIA_TYPE:
            rv.append(LOOKUP_DICT_MEDIA_TYPE[g])
        else:
            _log(path, line, f"unable to lookup media type: {g}")
    return rv


MISSING_COMMUNITIES: Counter[str] = Counter()


def _process_communities(
    path: Path,
    line: int,
    row: dict[str, str],
) -> tuple[list[URIRef], list[URIRef]]:
    supporting, recomending = [], []
    for community in _split(row.pop("Community")):
        match = COMMUNITY_RELATION_RE.search(community)
        if not match:
            _log(path, line, f'could not match regex for community "{community}"')
            continue

        name = match.group("name").strip()
        relation = match.group("relation")

        community_uuid = LOOKUP_DICT_COMMUNITIES.get(name, None)
        if not community_uuid:
            if not MISSING_COMMUNITIES[name]:
                _log(path, line, f"unknown community: {name}")
            MISSING_COMMUNITIES[name] += 1
            continue

        community_uriref = DALIA_COMMUNITY[community_uuid]

        for relation_char in relation:
            match relation_char:
                case "S":
                    supporting.append(community_uriref)
                case "R":
                    recomending.append(community_uriref)

    return supporting, recomending


def _process_related_works(
    path: Path,
    line: int,
    row: dict[str, str],
) -> list[PredicateObject[RDFResource]]:
    related_works = row.pop("RelatedWork")

    if not related_works.strip():
        return []

    rv: list[PredicateObject[RDFResource]] = []
    for related_work in related_works.split(DELIMITER):
        if not (related_work := related_work.strip()):
            raise Exception("Empty related work")

        related_work_substrings = related_work.split(":", maxsplit=1)

        relation = related_work_substrings[0].strip()
        relation_uriref = LOOKUP_DICT_RELATED_WORKS.get(relation, None)
        if not relation_uriref:
            raise Exception(f'Unknown related work relation "{relation}"')

        if len(related_work_substrings) < 2 or not (link := related_work_substrings[1].strip()):
            raise Exception(f'Link missing in related work "{related_work}"')

        rv.append(PredicateObject(predicate=relation_uriref, object=link))
    return rv

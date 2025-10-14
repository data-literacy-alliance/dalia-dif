"""Reader for DIF v1.3."""

import re
from collections import Counter
from pathlib import Path
from typing import TextIO

import click
import rdflib
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
    LEARNING_RESOURCE_TYPES,
    MEDIA_TYPES,
    PROFICIENCY_LEVELS,
    PROPRIETARY_LICENSE,
    RELATED_WORKS_RELATIONS,
    TARGET_GROUPS,
)
from ..namespace import DALIA_COMMUNITY, SPDX_LICENSE, bind
from ..utils import cleanup_languages

__all__ = [
    "parse_dif13_row",
    "read_dif13",
    "write_dif13_jsonl",
    "write_dif13_rdf",
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


def write_dif13_rdf(
    oers: EducationalResourceDIF13 | list[EducationalResourceDIF13],
    *,
    path: Path | None = None,
    format: str | None = None,
) -> None:
    """Write OERs as DIF v1.3 RDF."""
    if isinstance(oers, EducationalResourceDIF13):
        oers = [oers]
    graph = rdflib.Graph()
    bind(graph)
    for er in oers:
        graph += er.get_graph()
    if format is None:
        format = "turtle"
    if path is None:
        click.echo(graph.serialize(format=format))
    else:
        graph.serialize(path, format=format)


def write_dif13_jsonl(
    oers: EducationalResourceDIF13 | list[EducationalResourceDIF13], *, path: Path | None = None
) -> None:
    """Write OERs as DIF v1.3 JSON lines."""
    if isinstance(oers, EducationalResourceDIF13):
        oers = [oers]
    lines = (o.model_dump_json(exclude_none=True, exclude_defaults=True) for o in oers)
    if path is None:
        for line in lines:
            click.echo(line)
    else:
        with path.open("w") as file:
            file.write("\n".join(lines))


def read_dif13(path: str | Path | TextIO) -> list[EducationalResourceDIF13]:
    """Parse DALIA records."""
    if isinstance(path, str) and (path.startswith("http://") or path.startswith("https://")):
        from io import StringIO

        import requests

        with requests.get(path, timeout=5) as res:
            sio = StringIO(res.text)
            sio.name = path.split("/")[-1]
            return read_dif13(sio)

    if isinstance(path, (str, Path)):
        file_name = Path(path).name
    else:
        file_name = path.name
    with safe_open_dict_reader(path, delimiter=",") as reader:
        return [
            oer
            for idx, record in enumerate(reader, start=2)
            if (oer := parse_dif13_row(file_name, idx, record)) is not None
        ]


def parse_dif13_row(
    file_name: str, idx: int, row: dict[str, str], *, future: bool = False
) -> EducationalResourceDIF13 | None:
    """Convert a row in a DALIA curation file to a resource, or return none if unable."""
    supporting_communities, recommending_communities = _process_communities(file_name, idx, row)

    external_uris = _pop_split(row, "Link")
    if future and (n4c_id := row.pop("N4C_ID", None)):
        external_uris.append(n4c_id)

    title, _, subtitle = map(str.strip, row.pop("Title").partition(":"))

    uuid = row.pop("DALIA_ID", None) or row.pop("uuid", None)
    if not uuid:
        _log(file_name, idx, "no UUID given")
        return None

    try:
        rv = EducationalResourceDIF13(
            uuid=uuid,
            title=title,
            subtitle=subtitle or None,
            authors=_process_authors(file_name, idx, row),
            license=_process_license(row),
            links=external_uris,
            supporting_communities=supporting_communities,
            recommending_communities=recommending_communities,
            description=row.pop("Description").strip() or None,
            disciplines=_process_disciplines(file_name, idx, row),
            file_formats=_process_formats(row),
            keywords=_pop_split(row, "Keywords"),
            languages=_process_languages(row),
            learning_resource_types=_process_learning_resource_types(file_name, idx, row),
            media_types=_process_media_types(file_name, idx, row),
            proficiency_levels=_process_proficiency_levels(row),
            publication_date=_process_publication_date(row),
            target_groups=_process_target_groups(file_name, idx, row),
            related_works=_process_related_works(file_name, idx, row),
            file_size=_process_size(row),
            version=row.pop("Version") or None,
        )
    except ValueError as e:
        _log(getattr(file_name, "name", ""), idx, str(e))
        return None
    for k, v in row.items():
        if v and v.strip():
            UNPROCESSED[k] += 1
    return rv


def _pop_split(d: dict[str, str], key: str) -> list[str]:
    s = d.pop(key, None)
    if not s:
        return []
    return [y for x in s.split(DELIMITER) if (y := x.strip())]


def _log(file_name: str, line: int, text: str) -> None:
    tqdm.write(f"[{file_name} line:{line}] {text}")


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


def _process_disciplines(file_name: str, idx: int, row: dict[str, str]) -> list[URIRef]:
    rv = []
    for f in _pop_split(row, "Discipline"):
        if f.startswith("https://w3id.org/kim/hochschulfaechersystematik/"):
            rv.append(URIRef(f))
        else:
            _log(file_name, idx, f"invalid discipline: {f}")
    return rv


def _process_formats(row: dict[str, str]) -> list[str]:
    return [f.lstrip(".").upper() for f in _pop_split(row, "FileFormat")]


def _process_languages(row: dict[str, str]) -> list[ISO639_3]:
    return cleanup_languages(_pop_split(row, "Language"))


def _process_proficiency_levels(row: dict[str, str]) -> list[URIRef]:
    return [PROFICIENCY_LEVELS[x.lower()] for x in _pop_split(row, "ProficiencyLevel")]


def _process_authors(
    file_name: str, idx: int, row: dict[str, str]
) -> list[AuthorDIF13 | OrganizationDIF13]:
    return [
        author
        for s in _pop_split(row, "Authors")
        if (author := _process_author(file_name, idx, s)) is not None
    ]


def _process_author(file_name: str, idx: int, s: str) -> AuthorDIF13 | OrganizationDIF13 | None:
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
            _log(file_name, idx, f"invalid ORCID: {orcid}")
            return None
        family_name, _, given_name = (x.strip() for x in name.rpartition(","))
        return AuthorDIF13(
            given_name=given_name, family_name=family_name, orcid=ORCID_URI_PREFIX + orcid
        )
    elif url.startswith(ROR_URI_PREFIX):
        return OrganizationDIF13(name=name, ror=url.removeprefix(ROR_URI_PREFIX))

    _log(file_name, idx, f"failed to parse author: {s}")
    return None


def _process_license(row: dict[str, str]) -> str | URIRef | None:
    identifier = row.pop("License").strip()
    if identifier == "proprietary":
        return PROPRIETARY_LICENSE
    return SPDX_LICENSE[identifier]


def _process_target_groups(file_name: str, line: int, row: dict[str, str]) -> list[URIRef]:
    rv = []
    for g in _pop_split(row, "TargetGroup"):
        if g.lower() in TARGET_GROUPS:
            rv.append(TARGET_GROUPS[g.lower()])
        else:
            _log(file_name, line, f"unable to lookup target group: {g}")
    return rv


def _process_size(row: dict[str, str]) -> str | None:
    size = row.pop("Size")
    if not size:
        return None
    if size.endswith(" MB"):
        # FIXME should not be like this
        return size
    return f"{size} MB"


def _process_learning_resource_types(
    file_name: str, line: int, row: dict[str, str]
) -> list[URIRef]:
    rv = []
    for x in _pop_split(row, "LearningResourceType"):
        x = x.lower()
        if x.startswith("https://w3id.org/kim/hcrt/"):
            rv.append(URIRef(x))
        elif x in LEARNING_RESOURCE_TYPES:
            rv.append(LEARNING_RESOURCE_TYPES[x])
        else:
            _log(file_name, line, f"unable to lookup learning resource type: {x}")
    return rv


def _process_media_types(file_name: str, line: int, row: dict[str, str]) -> list[URIRef]:
    rv = []
    for g in _pop_split(row, "MediaType"):
        if g in MEDIA_TYPES:
            rv.append(MEDIA_TYPES[g])
        else:
            _log(file_name, line, f"unable to lookup media type: {g}")
    return rv


MISSING_COMMUNITIES: Counter[str] = Counter()


def _process_communities(
    file_name: str,
    line: int,
    row: dict[str, str],
) -> tuple[list[URIRef], list[URIRef]]:
    supporting, recommending = [], []
    for community in _pop_split(row, "Community"):
        match = COMMUNITY_RELATION_RE.search(community)
        if not match:
            _log(file_name, line, f'could not match regex for community "{community}"')
            continue

        name = match.group("name").strip()
        relation = match.group("relation")

        community_uuid = LOOKUP_DICT_COMMUNITIES.get(name, None)
        if not community_uuid:
            if not MISSING_COMMUNITIES[name]:
                _log(file_name, line, f"unknown community: {name}")
            MISSING_COMMUNITIES[name] += 1
            continue

        community_uriref = DALIA_COMMUNITY[community_uuid]

        for relation_char in relation:
            match relation_char:
                case "S":
                    supporting.append(community_uriref)
                case "R":
                    recommending.append(community_uriref)

    return supporting, recommending


def _process_related_works(
    file_name: str,
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
        relation_uriref = RELATED_WORKS_RELATIONS.get(relation, None)
        if not relation_uriref:
            _log(file_name, line, f'unknown related work relation "{relation}"')
            continue

        if len(related_work_substrings) < 2 or not (link := related_work_substrings[1].strip()):
            _log(file_name, line, f"related work is missing link: `{related_work}`")
            continue

        rv.append(PredicateObject(predicate=relation_uriref, object=link))
    return rv

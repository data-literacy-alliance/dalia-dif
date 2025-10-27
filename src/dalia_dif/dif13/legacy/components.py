"""A refactored legacy implementation parsing DIF v1.3 from Frank Lange."""

import re
from pathlib import Path

import click
from rdflib import XSD, Graph, Literal, Node, URIRef

from ..community import COMMUNITIES_PATH, LOOKUP_DICT_COMMUNITIES, MISSING_COMMUNITIES
from ..constants import DIF_SEPARATOR
from ..picklists import (
    COMMUNITY_RELATIONS,
    LEARNING_RESOURCE_TYPES,
    MEDIA_TYPE_EXCEPTIONS,
    MEDIA_TYPES,
    PROFICIENCY_LEVELS,
    PROPRIETARY_LICENSE,
    RELATED_WORKS_RELATIONS,
    TARGET_GROUPS,
)
from ..predicates import (
    DATE_PUBLISHED_PREDICATE,
    DESCRIPTION_PREDICATE,
    DISCIPLINE_PREDICATE,
    FILE_FORMAT_PREDICATE,
    FILE_SIZE_PREDICATE,
    KEYWORDS_PREDICATE,
    LANGUAGE_PREDICATE,
    LEARNING_RESOURCE_TYPE_PREDICATE,
    LICENSE_PREDICATE,
    LINK_PREDICATE,
    MEDIA_TYPES_PREDICATE,
    PROFICIENCY_LEVEL_PREDICATE,
    SUBTITLE_PREDICATE,
    TARGET_GROUP_PREDICATE,
    TITLE_PREDICATE,
    VERSION_PREDICATE,
)
from ..rdf import (
    check_discipline_exists,
    check_resource_type_exists,
    get_language_uriref,
    get_license_uriref,
)
from ...namespace import DALIA_COMMUNITY


def add_description_to_lr(g: Graph, lr_node: Node, description: str) -> None:
    if not (description := description.strip()):
        return
    g.add((lr_node, DESCRIPTION_PREDICATE, Literal(description)))


def add_file_formats_to_lr(g: Graph, lr_node: Node, file_formats: str) -> None:
    if not file_formats.strip():
        return

    for file_format in file_formats.split(DIF_SEPARATOR):
        if not (file_format := file_format.strip()):
            raise Exception("Empty file format")

        match = re.search(r"^\.?(?P<format>\S+)$", file_format)
        if not match:
            raise Exception(f'Could not match regex for file format "{file_format}"')
        fmt = match.group("format")

        g.add((lr_node, FILE_FORMAT_PREDICATE, Literal(fmt.upper())))


def add_keywords_to_lr(g: Graph, lr_node: Node, keywords: str) -> None:
    if not keywords.strip():
        return

    for keyword in keywords.split(DIF_SEPARATOR):
        if not (keyword := keyword.strip()):
            raise Exception("Empty keyword")

        g.add((lr_node, KEYWORDS_PREDICATE, Literal(keyword)))


def add_media_types_to_lr(g: Graph, lr_node: Node, media_types: str) -> None:
    if not media_types.strip():
        return

    for media_type in media_types.split(DIF_SEPARATOR):
        if not (media_type := media_type.strip()):
            raise Exception("Empty media type")

        media_type_uriref = MEDIA_TYPES.get(media_type.lower(), None)
        if not media_type_uriref:
            raise Exception(f'Unknown media type "{media_type}"')

        g.add((lr_node, MEDIA_TYPES_PREDICATE, media_type_uriref))


def add_proficiency_levels_to_lr(g: Graph, lr_node: Node, proficiency_levels: str) -> None:
    if not proficiency_levels.strip():
        return

    for proficiency_level in proficiency_levels.split(DIF_SEPARATOR):
        if not (proficiency_level := proficiency_level.strip()):
            raise Exception("Empty proficiency level")

        proficiency_level_uriref = PROFICIENCY_LEVELS.get(proficiency_level.lower(), None)
        if not proficiency_level_uriref:
            raise Exception(f'Unknown proficiency level "{proficiency_level}"')

        g.add((lr_node, PROFICIENCY_LEVEL_PREDICATE, proficiency_level_uriref))


def add_size_to_lr(g: Graph, lr_node: Node, size: str) -> None:
    if not (size := size.strip()):
        return

    float(size.split()[0])  # Validation: may rise ValueError

    g.add(
        (
            lr_node,
            FILE_SIZE_PREDICATE,
            Literal(f"{size} MB" if bool(re.fullmatch(r"\d+(\.\d+)?", size)) else size),
        )
    )


def add_target_groups_to_lr(g: Graph, lr_node: Node, target_groups: str) -> None:
    if not target_groups.strip():
        return

    for target_group in target_groups.split(DIF_SEPARATOR):
        if not (target_group := target_group.strip()):
            raise Exception("Empty target group")

        target_group_uriref = TARGET_GROUPS.get(target_group.lower(), None)
        if not target_group_uriref:
            raise Exception(f'Unknown target group "{target_group}"')

        g.add((lr_node, TARGET_GROUP_PREDICATE, target_group_uriref))


def add_title_to_lr(g: Graph, lr_node: Node, title: str) -> None:
    if not (title := title.strip()):
        raise Exception("Empty Title field")

    title_substrings = title.split(": ", maxsplit=1)

    g.add((lr_node, TITLE_PREDICATE, Literal(title_substrings[0].strip())))

    if len(title_substrings) > 1 and (subtitle := title_substrings[1].strip()):
        g.add((lr_node, SUBTITLE_PREDICATE, Literal(subtitle)))


def add_related_works_to_lr(g: Graph, lr_node: Node, related_works: str) -> None:
    if not related_works.strip():
        return

    for related_work in related_works.split(DIF_SEPARATOR):
        if not (related_work := related_work.strip()):
            raise Exception("Empty related work")

        related_work_substrings = related_work.split(":", maxsplit=1)

        relation = related_work_substrings[0].strip()
        relation_uriref = RELATED_WORKS_RELATIONS.get(relation, None)
        if not relation_uriref:
            raise Exception(f'Unknown related work relation "{relation}"')

        if len(related_work_substrings) < 2 or not (link := related_work_substrings[1].strip()):
            raise Exception(f'Link missing in related work "{related_work}"')

        g.add((lr_node, relation_uriref, URIRef(link)))


def add_links_to_lr(g: Graph, lr_node: Node, links: str) -> None:
    if not links.strip():
        raise Exception("Empty Link field")

    for link in links.split(DIF_SEPARATOR):
        if not (link := link.strip()):
            raise Exception("Empty link")

        g.add((lr_node, LINK_PREDICATE, URIRef(link)))


def add_version_to_lr(g: Graph, lr_node: Node, version: str) -> None:
    if not (version := version.strip()):
        return

    g.add((lr_node, VERSION_PREDICATE, Literal(version)))


def add_disciplines_to_lr(
    g: Graph, lr_node: Node, disciplines: str, row_number: int = 0, path: Path | None = None
) -> None:
    if not disciplines.strip():
        return

    for discipline in disciplines.split(DIF_SEPARATOR):
        if not (discipline := discipline.strip()):
            raise Exception("Empty discipline")

        discipline_uriref = URIRef(discipline)
        if not check_discipline_exists(discipline_uriref):
            raise ValueError(
                f'[{path} line:{row_number:,}] discipline "{discipline}" does not exist in the Hochschulfaechersystematik'
            )

        g.add((lr_node, DISCIPLINE_PREDICATE, discipline_uriref))


def add_license_to_lr(g: Graph, lr_node: Node, license_: str) -> None:
    if not (license_ := license_.strip()):
        raise Exception("Empty License field")

    license_uri: URIRef | None
    if license_ == "proprietary":
        license_uri = PROPRIETARY_LICENSE
    else:
        license_uri = get_license_uriref(license_)
    if not license_uri:
        raise Exception(f'Invalid license identifier "{license_}". Please check SPDX.')

    g.add((lr_node, LICENSE_PREDICATE, license_uri))


def add_languages_to_lr(g: Graph, lr_node: Node, languages: str) -> None:
    if not languages.strip():
        return

    for language in languages.split(DIF_SEPARATOR):
        if not (language := language.strip()):
            raise Exception("Empty language")

        language_uri = get_language_uriref(language)
        if not language_uri:
            raise Exception(f'Invalid language identifier "{language}". Please check Lexvo.')

        g.add((lr_node, LANGUAGE_PREDICATE, language_uri))


def add_publication_date_to_lr(g: Graph, lr_node: Node, publication_date: str) -> None:
    if not (publication_date := publication_date.strip()):
        return
    d = _date_to_literal(publication_date)
    if d is None:
        raise ValueError(f'Invalid publication date "{publication_date}"')
    g.add((lr_node, DATE_PUBLISHED_PREDICATE, d))


def _date_to_literal(s: str) -> Literal | None:
    # regex from https://stackoverflow.com/a/22061879
    # YYYY-MM-DD
    if re.search(r"^\d{4}-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])$", s):
        return Literal(s, datatype=XSD.date)
    # YYYY-MM
    if re.search(r"^\d{4}-(0[1-9]|1[012])$", s):
        return Literal(s, datatype=XSD.gYearMonth)
    # YYYY
    if re.search(r"^\d{4}$", s):
        return Literal(s, datatype=XSD.gYear)
    # DD.MM.YYYY
    if re.search(r"^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[012])\.\d{4}$", s):
        parts = s.split(".")
        s = f"{parts[2]}-{parts[1]}-{parts[0]}"
        return Literal(s, datatype=XSD.date)
    # MM.YYYY
    if re.search(r"^(0[1-9]|1[012])\.\d{4}$", s):
        parts = s.split(".")
        s = f"{parts[1]}-{parts[0]}"
        return Literal(s, datatype=XSD.gYearMonth)
    return None


def add_learning_resource_types_to_lr(
    g: Graph,
    lr_node: Node,
    learning_resource_types: str,
    row_number: int = 0,
    path: Path | None = None,
) -> None | list[URIRef | None]:
    if not learning_resource_types.strip():
        return None

    rv: list[URIRef | None] = []
    for learning_resource_type in learning_resource_types.split(DIF_SEPARATOR):
        if not (learning_resource_type := learning_resource_type.strip()):
            raise Exception("Empty learning resource type")

        lr_type_uriref = LEARNING_RESOURCE_TYPES.get(learning_resource_type.lower(), None)
        if not lr_type_uriref:
            # Try to find it in the HCRT vocabulary.
            hcrt_term = URIRef(learning_resource_type)
            if check_resource_type_exists(hcrt_term):
                lr_type_uriref = hcrt_term

        if not lr_type_uriref:
            raise ValueError(f'Unknown learning resource type "{learning_resource_type}"')

        if lr_type_uriref in MEDIA_TYPE_EXCEPTIONS:
            if path:
                lead = f"[{path.name} line:{row_number}]"
            else:
                lead = f"[{row_number}]"

            click.secho(
                f'{lead} rather than using "{learning_resource_type}" resource type, consider '
                f'using media type "{MEDIA_TYPE_EXCEPTIONS[lr_type_uriref]}"',
                fg="yellow",
            )
            continue

        g.add((lr_node, LEARNING_RESOURCE_TYPE_PREDICATE, lr_type_uriref))
        rv.append(lr_type_uriref)
    return rv


def add_communities_to_lr(
    g: Graph, lr_node: Node, communities: str, *, row_number: int = 0, path: Path | None = None
) -> None:
    if not communities.strip():
        return

    for community in communities.split(DIF_SEPARATOR):
        if not (community := community.strip()):
            raise Exception("Empty community")

        match = re.search(r"^(?P<name>.*)\s\((?P<relation>S|R|SR|RS)\)$", community)
        if not match:
            raise ValueError(
                f'[line:{row_number:,}] Community was incorrectly encoded "{community}". Did you remember to '
                f"include one of (S), (R), (SR), or (RS) at the end?"
            )

        name = match.group("name").strip()
        relation = match.group("relation")

        community_id = LOOKUP_DICT_COMMUNITIES.get(name, None)
        if not community_id:
            if not MISSING_COMMUNITIES[name]:
                msg = f'unknown community "{name}".\n\tSuggestion: add to {COMMUNITIES_PATH.name}'
                if path:
                    msg = f"[{path.name}] {msg}"
                raise ValueError(msg)
            MISSING_COMMUNITIES[name] += 1
            return
        community_uriref = DALIA_COMMUNITY[community_id]

        for relation_char in relation:
            relation_uriref = COMMUNITY_RELATIONS[relation_char]
            g.add((lr_node, relation_uriref, community_uriref))

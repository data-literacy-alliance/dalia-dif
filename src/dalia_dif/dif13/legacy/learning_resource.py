"""A refactored legacy implementation parsing DIF v1.3 from Frank Lange."""

from pathlib import Path
from uuid import UUID

import click
from pystow.utils import safe_open_dict_reader
from rdflib import RDF, Graph
from tqdm import tqdm

from .authors import add_authors_to_lr
from .components import (
    add_communities_to_lr,
    add_description_to_lr,
    add_disciplines_to_lr,
    add_file_formats_to_lr,
    add_keywords_to_lr,
    add_languages_to_lr,
    add_learning_resource_types_to_lr,
    add_license_to_lr,
    add_links_to_lr,
    add_media_types_to_lr,
    add_proficiency_levels_to_lr,
    add_publication_date_to_lr,
    add_related_works_to_lr,
    add_size_to_lr,
    add_target_groups_to_lr,
    add_title_to_lr,
    add_version_to_lr,
)
from .. import constants
from ..constants import DIF_HEADER_ID
from ..predicates import EDUCATIONAL_RESOURCE_CLASS
from ...namespace import DALIA_OER, get_base_graph

__all__ = [
    "parse_dif13_row_legacy",
    "read_dif13",
]


def read_dif13(filename: str | Path, *, sep: str = ",") -> tuple[bool, Graph]:
    """Read a CSV containing DIF v1.3 encoded content.

    :param filename: The local filepath.
    :param sep: The seperator for the CSV file.

    :returns: A pair of a boolean "has error" and a RDFlib graph
    """
    has_error = False
    collection_graph = get_base_graph()

    path = Path(filename).expanduser().resolve()
    with safe_open_dict_reader(path, delimiter=sep) as reader:
        if DIF_HEADER_ID not in set(reader.fieldnames):  # type:ignore[arg-type]
            has_error = True
            tqdm.write(click.style(f"no {DIF_HEADER_ID} column found in {path}", fg="red"))
            return has_error, collection_graph

        for row_number, row in enumerate(reader, start=2):
            try:
                parse_dif13_row_legacy(collection_graph, row_number, _trim_row(row), path=path)
            except Exception as e:
                tqdm.write(click.style(f"{e!s}", fg="red"))
                if isinstance(e, KeyError):
                    raise ValueError("This could be due to an incorrect column name.") from None
                has_error = True

    return has_error, collection_graph


def _trim_row(row: dict[str, str]) -> dict[str, str]:
    return {k: v.strip() for k, v in row.items()}


def parse_dif13_row_legacy(
    g: Graph, row_number: int, row: dict[str, str], path: Path | None = None
) -> None:
    if not (lr_id := row[constants.DIF_HEADER_ID].strip()):
        tqdm.write(
            click.style(
                f"[{row_number}] Empty {constants.DIF_HEADER_ID} field - ignoring this row",
                fg="yellow",
            )
        )
        return None

    uuid = UUID(lr_id)  # Validation: may rise ValueError
    lr_node = DALIA_OER[str(uuid)]
    g.add((lr_node, RDF.type, EDUCATIONAL_RESOURCE_CLASS))

    add_authors_to_lr(
        g, lr_node, row[constants.DIF_HEADER_AUTHORS], row_number=row_number, path=path
    )
    add_license_to_lr(g, lr_node, row[constants.DIF_HEADER_LICENSE])
    add_links_to_lr(g, lr_node, row[constants.DIF_HEADER_LINK])
    add_title_to_lr(g, lr_node, row[constants.DIF_HEADER_TITLE])
    add_communities_to_lr(
        g, lr_node, row[constants.DIF_HEADER_COMMUNITY], row_number=row_number, path=path
    )
    add_description_to_lr(g, lr_node, row[constants.DIF_HEADER_DESCRIPTION])
    add_disciplines_to_lr(
        g, lr_node, row[constants.DIF_HEADER_DISCIPLINE], row_number=row_number, path=path
    )
    add_file_formats_to_lr(g, lr_node, row[constants.DIF_HEADER_FILE_FORMAT])
    add_keywords_to_lr(g, lr_node, row[constants.DIF_HEADER_KEYWORDS])
    add_languages_to_lr(g, lr_node, row[constants.DIF_HEADER_LANGUAGE])
    add_learning_resource_types_to_lr(
        g,
        lr_node,
        row[constants.DIF_HEADER_LEARNING_RESOURCE_TYPE],
        row_number=row_number,
        path=path,
    )
    add_media_types_to_lr(g, lr_node, row[constants.DIF_HEADER_MEDIA_TYPE])
    add_proficiency_levels_to_lr(g, lr_node, row[constants.DIF_HEADER_PROFICIENCY_LEVEL])
    add_publication_date_to_lr(g, lr_node, row[constants.DIF_HEADER_PUBLICATION_DATE])
    add_target_groups_to_lr(g, lr_node, row[constants.DIF_HEADER_TARGET_GROUP])
    add_related_works_to_lr(g, lr_node, row[constants.DIF_HEADER_RELATED_WORK])
    add_size_to_lr(g, lr_node, row[constants.DIF_HEADER_SIZE])
    add_version_to_lr(g, lr_node, row[constants.DIF_HEADER_VERSION])

    return None

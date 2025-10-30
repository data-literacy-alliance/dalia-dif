"""Full-text indexing utilities.

This module contains the functions for generating a full text index in SQLite from open
educational resources encoded in RDF using the DIF v1.3 schema.

.. code-block:: python

    from dalia_ingest.model import dif13_to_sqlite_fti, query_sqlite_fti

    # give a path or list of paths to TTL files to parse
    ttl_path = ...

    # constructs an in-memory database, should be done once
    # during startup of the backend
    conn = dif13_to_sqlite_fti(ttl_path)

    # many queries can be made over the same in-memory,
    # database object. ``*`` can be used as a wildcard at
    # the end (but not the beginning) of the string
    uuids = query_sqlite_fti("chem*", conn)
"""

from __future__ import annotations

import sqlite3
from collections import defaultdict
from contextlib import closing
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import rdflib

from dalia_dif.namespace import DALIA_OER

if TYPE_CHECKING:
    import pandas

__all__ = [
    "dif13_to_sqlite_fti",
    "query_sqlite_fti",
    "write_sqlite_fti",
]


def query_sqlite_fti(query: str, db: str | Path | sqlite3.Connection) -> list[str]:
    """Get UUIDs for documents matching the query.

    :param query: The query string, like `chem`. Can also include wildcards like in
        `chem*`.
    :param db: Either a path to a SQLite database file or an already-established
        connection

    :returns: A list of UUIDs for OERs that match the query
    """
    sql = _get_fts_sql(query)

    if isinstance(db, str | Path):
        db = Path(db).expanduser().resolve()
        with closing(sqlite3.connect(db.as_posix())) as conn, closing(conn.cursor()) as cursor:
            results = cursor.execute(sql).fetchall()
    elif isinstance(db, sqlite3.Connection):
        with closing(db.cursor()) as cursor:
            results = cursor.execute(sql).fetchall()
    else:
        raise TypeError

    # unpack UUIDs and throw away scores
    return [uuid for uuid, _score in results]


def _get_fts_sql(query: str) -> str:
    # Test FTS query (e.g., search all fields for "python") note that the bm25 weights
    return dedent(f"""\
        SELECT uuid, bm25(documents, 0.0, 5.0, 1.0, 0.5)
        FROM documents
        WHERE documents MATCH '{query}'
        ORDER BY rank;
    """)  # noqa:S608


def dif13_to_sqlite_fti(paths: str | Path | list[str | Path]) -> sqlite3.Connection:
    """Construct an in-memory SQLite database with a full-text index over OERs encoded in DIF v1.3.

    :param paths: The path or paths to turtle files encoding OERs in DIF v1.3

    :returns: An in-memory SQLite database object that can be queried

    Example usage:

    .. code-block:: python

        ttl_path = ...
        conn = dif13_to_sqlite_fti(ttl_path)
        uuids = query_sqlite_fti("chem*", conn)
    """
    graph = rdflib.Graph()

    if isinstance(paths, str | Path):
        graph.parse(paths)
    elif isinstance(paths, list):
        for path in paths:
            graph.parse(path)
    else:
        raise TypeError(f"`paths` should be a path or list of paths. Got: ({type(paths)}) {paths}")

    return graph_to_conn(graph)


def graph_to_conn(graph: rdflib.Graph) -> sqlite3.Connection:
    df = graph_to_df(graph)
    conn = sqlite3.connect(":memory:")
    _dif13_df_to_sqlite(df, conn)
    return conn


def graph_to_df(graph: rdflib.Graph) -> pandas.DataFrame:
    import pandas as pd

    titles = defaultdict(set)
    descriptions = defaultdict(set)
    keywords = defaultdict(set)
    for uri, title, description, keyword in list(  # type:ignore[misc]
        graph.query(DIF13_DISCIPLINE_PREDICATE_SPARQL_QUERY)
    ):
        uuid = uri.removeprefix(str(DALIA_OER))
        if title:
            titles[uuid].add(title)
        if description:
            descriptions[uuid].add(description)
        if keyword:
            keywords[uuid].add(keyword)

    rows = [
        (
            uuid,
            " ".join(titles.get(uuid, [])),
            " ".join(descriptions.get(uuid, [])),
            " ".join(keywords.get(uuid, [])),
        )
        for uuid in set(titles).union(descriptions).union(keywords)
    ]
    df = pd.DataFrame(rows, columns=["uuid", "title", "description", "keywords"])
    return df


#: Query RDF encoded in DIF v1.3 for an OER's identifier, title, description, and keywords
DIF13_DISCIPLINE_PREDICATE_SPARQL_QUERY = """\
SELECT
    ?oer
    ?title
    ?description
    ?keyword
WHERE {
    ?oer a educor:EducationalResource .
    OPTIONAL { ?oer dcterms:title ?title . }
    OPTIONAL { ?oer dcterms:description ?description . }
    OPTIONAL { ?oer schema:keywords ?keyword . }
}
"""


def _dif13_df_to_sqlite(df: pandas.DataFrame, conn: sqlite3.Connection) -> None:
    """Write a dataframe to a SQLite database (which could be in-memory)."""
    # Enable FTS5 extension (usually built-in with modern SQLite)
    # Create FTS5 virtual table
    query = dedent("""\
        CREATE VIRTUAL TABLE documents USING fts5(
            uuid,
            title,
            description,
            keywords,
            prefix='2 3 4 5 6',
            tokenize = 'porter'
        )
    """)
    with closing(conn.cursor()) as cursor:
        cursor.execute(query)
    df.to_sql("documents", conn, if_exists="append", index=False)


def write_sqlite_fti(graph: rdflib.Graph, path: Path) -> None:
    """Write a SQLite database with a full text index."""
    df = graph_to_df(graph)
    with closing(sqlite3.connect(path.as_posix())) as conn:
        _dif13_df_to_sqlite(df, conn)

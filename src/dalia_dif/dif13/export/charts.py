# mypy: disable-error-code="misc"

"""Summarize from RDF."""

from __future__ import annotations

import datetime
from collections import Counter, defaultdict
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, Any

import click
import rdflib

from dalia_dif.dif13.community import get_community_labels
from dalia_dif.dif13.predicates import RECOMMENDING_COMMUNITY_PRED, SUPPORTING_COMMUNITY_PRED
from dalia_dif.dif13.rdf import get_discipline_graph
from dalia_dif.namespace import CONVERTER

if TYPE_CHECKING:
    import matplotlib.axes

__all__ = [
    "export_chart",
]

MISSING = "missing"

COUNT_OERS_SPARQL = dedent("""\
    SELECT DISTINCT (COUNT(?s) as ?count)
    WHERE {
        ?s a educor:EducationalResource .
    }
    GROUP BY ?S
""")


def count_oers(graph: rdflib.Graph) -> int:
    """Count OERs."""
    res = graph.query(COUNT_OERS_SPARQL)
    rv = int(str(next(iter(res))[0]))  # type:ignore[index]
    return rv


COUNT_LANGUAGES_SPARQL = dedent("""\
    SELECT ?s ?o
    WHERE {
        ?s a educor:EducationalResource .
        ?s dcterms:language ?o .
    }
""")


def count_languages(graph: rdflib.Graph, *, upper: int = 4) -> tuple[Counter[str], Counter[str]]:
    """Count languages."""
    res = list(graph.query(COUNT_LANGUAGES_SPARQL))
    if len(res) == 0:
        raise ValueError(f"query returned no results:\n{COUNT_LANGUAGES_SPARQL}")
    dd = defaultdict(list)
    for uuid, lang in res:
        dd[uuid].append(str(lang).removeprefix("http://lexvo.org/id/iso639-3/"))
    combine: Counter[str] = Counter(
        ", ".join(sorted(v)) if len(v) < upper else f"eng + {len(v) - 1}" if "eng" in v else len(v)
        for v in dd.values()
    )
    single: Counter[str] = Counter(s for v in dd.values() for s in v)
    return combine, single


COUNT_LICENSES_SPARQL = dedent("""\
    SELECT ?o
    WHERE {
        ?s a educor:EducationalResource .
        ?s dcterms:license ?o .
    }
""")


def count_licenses(graph: rdflib.Graph) -> Counter[str]:
    """Count licenses."""
    res = list(graph.query(COUNT_LICENSES_SPARQL))
    if len(res) == 0:
        raise ValueError(f"query returned no results:\n{COUNT_LICENSES_SPARQL}")
    return Counter(
        CONVERTER.compress(license_uri, strict=False, passthrough=True)
        .removeprefix("spdx:")
        .removeprefix("spdx.license:")
        .removesuffix("-3.0")
        .removesuffix("-4.0")
        .removesuffix("-2.0")
        .removesuffix("-1.0")
        .replace("modalia:ProprietaryLicense", "proprietary")
        for (license_uri,) in res
    )


COUNT_FILE_EXTENSIONS_SPARQL = dedent("""\
    SELECT ?s ?o
    WHERE {
        ?s a educor:EducationalResource .
        OPTIONAL { ?s dcterms:format ?o . }
    }
""")


def count_file_extensions(graph: rdflib.Graph) -> Counter[str]:
    """Count file extensions."""
    res = list(graph.query(COUNT_FILE_EXTENSIONS_SPARQL))
    if len(res) == 0:
        raise ValueError(f"query returned no results:\n{COUNT_FILE_EXTENSIONS_SPARQL}")
    return Counter(str(format_str) if format_str else MISSING for _, format_str in res)


MEDIA_TYPE_LABELS = {
    "schema:VideoObject": "video",
    "schema:Text": "text",
    "schema:PresentationDigitalDocument": "presentation",
    "schema:AudioObject": "audio",
    "modalia:Multipart": "multipart",
    "schema:ImageObject": "image",
    "modalia:Code": "code",
}

COUNT_MEDIA_TYPE_SPARQL = dedent("""\
SELECT ?o
WHERE {
    ?s a educor:EducationalResource .
    ?s modalia:hasMediaType ?o .
}
""")


def count_media_types(graph: rdflib.Graph) -> Counter[str]:
    """Count media types."""
    res = list(graph.query(COUNT_MEDIA_TYPE_SPARQL))
    if len(res) == 0:
        raise ValueError(f"query returned no results:\n{COUNT_MEDIA_TYPE_SPARQL}")
    return Counter(
        MEDIA_TYPE_LABELS[CONVERTER.compress(media_type, strict=True)].title()
        if media_type
        else MISSING
        for (media_type,) in res
    )


COUNT_TARGET_GROUPS_SPARQL = dedent("""\
    SELECT ?o
    WHERE {
        ?s a educor:EducationalResource .
        ?s modalia:hasTargetGroup ?o .
    }
""")


def count_target_groups(graph: rdflib.Graph, total: int) -> Counter[str]:
    """Count target groups."""
    res = list(graph.query(COUNT_TARGET_GROUPS_SPARQL))
    if len(res) == 0:
        raise ValueError(f"query returned no results:\n{COUNT_TARGET_GROUPS_SPARQL}")
    rv = Counter(
        _remap_target_group(CONVERTER.parse_uri(target_group, strict=True).identifier)
        if target_group
        else MISSING
        for (target_group,) in res
    )

    most, count = rv.most_common(1)[0]
    click.echo(f"The largest target group was {most} ({count:,}/{total:,}; {count / total:.1%})")
    return rv


TARGET_GROUP_RENAMES = {
    "PhDStudent": "PhD Student",
    "MastersStudent": "Master Student",
    "BachelorStudent": "Bachelor Student",
    "StudentSchool": "Bachelor Student",
    "DataSteward": "Data Steward",
    "TeacherHighEducation": "Teacher (Higher Ed.)",
    "TeacherSchool": "Teacher (Lower Ed.)",
    "ContentProvider": "Content Provider",
}


def _remap_target_group(x: str) -> str:
    return TARGET_GROUP_RENAMES.get(x, x)


LRT_MAPPING = {
    "PodcastSeries": "podcast",
    "drill_and_practice": "drill and practice",
    "bestpractices": "best practices",
    "Bestpractices": "best practices",
    "codenotebook": "code notebook",
    "Codenotebook": "code notebook",
    "SoftwareSourceCode": "code",
    "softwaresourcecode": "code",
    "Softwaresourcecode": "code",
}

COUNT_LEARNING_TYPE_RESOURCES_SPARQL = dedent("""\
    SELECT ?o
    WHERE {
        ?s a educor:EducationalResource .
        ?s modalia:hasLearningType ?o .
    }
""")


def count_learning_resource_type(graph: rdflib.Graph) -> Counter[str]:
    """Count learning resource type."""
    res = list(graph.query(COUNT_LEARNING_TYPE_RESOURCES_SPARQL))
    if len(res) == 0:
        raise ValueError(f"query returned no results:\n{COUNT_LEARNING_TYPE_RESOURCES_SPARQL}")
    return Counter(
        _remap_lrt(CONVERTER.parse_uri(learning_resource_type, strict=True).identifier)
        if learning_resource_type
        else MISSING
        for (learning_resource_type,) in res
    )


def _remap_lrt(x: str) -> str:
    return LRT_MAPPING.get(x, x).replace("_", " ").title()


DISCIPLINES_RENAMES = {
    "Cultural Studies in the narrower sense": "Cultural Studies",
    "Archival and Documentation Science": "Archival/Docs",
    "Human Medicine / Health Sciences": "Health Sciences",
    "Information and Library Sciences": "Library Sciences",
    "Geosciences (excl. Geography)": "Geosciences",
    "Agricultural Science/Agriculture": "Agriculture",
    "Mathematics, Natural Sciences": "Mathematics",
    "Medicine (General Medicine)": "Medicine",
    "Film and Television Studies": "Film Studies",
    "Art History, Art Theory": "Art History",
    "Art, Art Theory": "Art",
    "Social Sciences/Sociology": "Social Sciences",
    "Engineering Sciences": "Engineering",
    "Educational Sciences": "Education",
}

GET_DISCIPLINE_LABEL_SPARQL = dedent("""\
    SELECT ?s ?label WHERE {
        ?s <http://www.w3.org/2004/02/skos/core#prefLabel> ?label .
    }
""")


def get_discipline_names() -> dict[str, str]:
    """Get discipline names (LUID to name map for HSFS)."""
    dd: defaultdict[str, list[tuple[str | None, str]]] = defaultdict(list)
    for iri, label in get_discipline_graph().query(GET_DISCIPLINE_LABEL_SPARQL):
        if not isinstance(label, rdflib.Literal):
            raise ValueError
        luid = iri.removeprefix("https://w3id.org/kim/hochschulfaechersystematik/")
        dd[luid].append((label._language, DISCIPLINES_RENAMES.get(label._value, label._value)))
    return {k: min(v, key=_get_best_lang)[1] for k, v in dd.items()}


def _get_best_lang(pair: tuple[str | None, Any]) -> tuple[int, str]:
    if pair[0] == "en" or pair[0] is None:
        return 0, ""
    elif pair[0] == "de":
        return 1, ""
    else:
        return 2, pair[0]


COUNT_PROFICIENCY_LEVELS_SPARQL = dedent("""\
    SELECT ?s ?o
    WHERE {
        ?s a educor:EducationalResource .
        OPTIONAL { ?s modalia:requiresProficiencyLevel ?o . }
    }
""")


def count_proficiency_level(graph: rdflib.Graph, total: int) -> Counter[str]:
    """Count proficiency level."""
    res = list(graph.query(COUNT_PROFICIENCY_LEVELS_SPARQL))
    if len(res) == 0:
        raise ValueError(f"query returned no results:\n{COUNT_PROFICIENCY_LEVELS_SPARQL}")
    rv = Counter(
        CONVERTER.parse_uri(proficiency_level, strict=True).identifier.title()
        if proficiency_level
        else MISSING
        for subj, proficiency_level in res
    )

    most, count = rv.most_common(1)[0]
    click.echo(
        f"The largest proficiency level was {most} ({count:,}/{total:,}; {count / total:.1%})"
    )
    return rv


COUNT_DISCIPLINES_SPARQL = dedent("""\
    SELECT ?o
    WHERE {
        ?s a educor:EducationalResource .
        ?s <http://purl.org/spar/fabio/hasDiscipline> ?o .
    }
""")


def count_disciplines(graph: rdflib.Graph) -> Counter[str]:
    """Count disciplines."""
    res = list(graph.query(COUNT_DISCIPLINES_SPARQL))
    if len(res) == 0:
        raise ValueError(f"query returned no results:\n{COUNT_DISCIPLINES_SPARQL}")
    names = get_discipline_names()
    rv = Counter(
        names[CONVERTER.parse_uri(discipline, strict=True).identifier] for (discipline,) in res
    )
    frv: Counter[str] = Counter()
    for k, v in rv.most_common():
        if v > 1:
            frv[k] = v
        else:
            frv["Other"] += v
    return frv


COUNT_COMMUNITIES_SPARQL = dedent(f"""\
    SELECT ?o
    WHERE {{
        ?s a educor:EducationalResource .
        ?s ?p ?o
        VALUES ?p {{ <{SUPPORTING_COMMUNITY_PRED}> <{RECOMMENDING_COMMUNITY_PRED}> }}
    }}
""")


def count_communities(graph: rdflib.Graph) -> Counter[str]:
    """Count communities."""
    community_labels = get_community_labels()
    res = list(graph.query(COUNT_COMMUNITIES_SPARQL))
    if len(res) == 0:
        raise ValueError(f"query returned no results:\n{COUNT_COMMUNITIES_SPARQL}")
    # TODO this should be in the graph!
    rv = Counter(
        community_labels[str(community).removeprefix("https://id.dalia.education/community/")]
        for (community,) in res
    )
    for k, v in rv.most_common():
        if v < 3:
            rv["Other"] += v
            del rv[k]
    return rv


def barplot_counter(
    counter: Counter[str],
    *,
    ax: matplotlib.axes.Axes | None = None,
    title: str | None = None,
    log: bool = True,
    total: int,
) -> matplotlib.axes.Axes:
    """Plot a counter."""
    import seaborn as sns

    categories, counts = zip(*counter.most_common(), strict=False)
    ax = sns.barplot(y=categories, x=counts, ax=ax)

    max_width = max(patch.get_width() for patch in ax.patches)

    # Define threshold as a fraction of max width
    threshold = max_width * 0.45

    for patch in ax.patches:
        count = int(patch.get_width())
        label = f"{count} ({count / total:.1%})"
        y_pos = patch.get_y() + patch.get_height() / 2

        if count > threshold:
            # divide to move to the left, since it's on a log scale
            x_pos = count / 1.1
            color = "white"
            horizontal_alignment = "right"
        else:
            # multiple to move to the right, since it's on a log scale
            x_pos = count * 1.1
            color = "black"
            horizontal_alignment = "left"

        ax.text(
            x_pos,
            y_pos,
            label,
            ha=horizontal_alignment,
            va="center",
            color=color,
            fontweight="semibold",
            fontsize=10,
        )

    if title:
        ax.set_title(title)
    if log:
        ax.set_xscale("log")
    return ax


def export_chart(graph: rdflib.Graph, paths: Path | list[Path]) -> None:
    """Export the chart."""
    import matplotlib.pyplot as plt

    n_oers = count_oers(graph)
    click.secho(f"DALIA has {n_oers:,} OERs")

    _fig, axes = plt.subplots(3, 3, figsize=(15, 17))

    _combine_language_counter, single_language_counter = count_languages(graph)
    barplot_counter(
        single_language_counter, ax=axes[0][0], title="Language Occurrence", total=n_oers
    )
    barplot_counter(count_licenses(graph), ax=axes[0][1], title="Licenses", total=n_oers)
    barplot_counter(
        count_file_extensions(graph), ax=axes[0][2], title="File Extensions", total=n_oers
    )
    barplot_counter(count_media_types(graph), ax=axes[1][0], title="Media Types", total=n_oers)
    barplot_counter(
        count_proficiency_level(graph, n_oers),
        ax=axes[1][1],
        title="Required Proficiency Level",
        total=n_oers,
    )
    barplot_counter(count_disciplines(graph), ax=axes[1][2], title="Disciplines", total=n_oers)
    barplot_counter(count_communities(graph), ax=axes[2][0], title="Community", total=n_oers)
    barplot_counter(
        count_target_groups(graph, n_oers), ax=axes[2][1], title="Target Groups", total=n_oers
    )
    barplot_counter(
        count_learning_resource_type(graph),
        ax=axes[2][2],
        title="Learning Resource Type",
        total=n_oers,
    )

    today = datetime.date.today()

    plt.suptitle(f"A summary of {n_oers} OERs ({today.isoformat()})", fontsize=30, y=0.95)
    plt.subplots_adjust(top=0.85)  # move plot down a bit to create space below the suptitle
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # ensure layout doesn't overlap with suptitle

    if not isinstance(paths, list):
        paths = [paths]
    for path in paths:
        plt.savefig(path, dpi=300)
    plt.close()

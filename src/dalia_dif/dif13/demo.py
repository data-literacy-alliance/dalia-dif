"""Demo construction of DIF v1.3 OER."""

from pydantic_metamodel.api import PredicateObject

from .model import AuthorDIF13, EducationalResourceDIF13, OrganizationDIF13
from .picklists import (
    LOOKUP_DICT_MEDIA_TYPE,
    LOOKUP_DICT_PROFICIENCY_LEVEL,
    LOOKUP_DICT_RELATED_WORKS,
    LOOKUP_DICT_TARGET_GROUP,
)
from ..namespace import CONVERTER, HSFS


def _main() -> None:
    import click

    resource = EducationalResourceDIF13(
        uuid="b37ddf6e-f136-4230-8418-faf18c4c34d2",
        title="Chemotion ELN Instruction Videos",
        description="Chemotion ELN Instruction Videos Chemotion[1] is an open source "
        "system for storing and managing experiments and molecular data in "
        "chemistry and its related sciences.",
        links=["https://doi.org/10.5281/zenodo.7634481"],
        authors=[
            AuthorDIF13(given_name="Fabian", family_name="Fink", orcid="0000-0002-1863-2087"),
            AuthorDIF13(given_name="Salim", family_name="Benjamaa", orcid="0000-0001-6215-6834"),
            AuthorDIF13(given_name="Nicole", family_name="Parks", orcid="0000-0002-6243-2840"),
            AuthorDIF13(
                given_name="Alexander", family_name="Hoffmann", orcid="0000-0002-9647-8839"
            ),
            AuthorDIF13(
                given_name="Sonja", family_name="Herres-Pawlis", orcid="0000-0002-4354-4353"
            ),
        ],
        license="https://creativecommons.org/licenses/by/4.0",
        supporting_communities=[],
        recommending_communities=[OrganizationDIF13(name="NFDI4Chem", ror="05wwzbv21")],
        disciplines=[
            HSFS["n40"],  # chemistry
        ],
        file_formats=[
            ".mp4",
        ],
        keywords=["research data management", "NFDI", "RDM", "FDM", "NFDI4Chem", "Chemotion"],
        languages=["eng"],
        learning_resource_types=[],
        media_types=[
            LOOKUP_DICT_MEDIA_TYPE["video"],
        ],
        proficiency_levels=[
            LOOKUP_DICT_PROFICIENCY_LEVEL["novice"],
        ],
        publication_date="2023-02-13",
        target_groups=[
            LOOKUP_DICT_TARGET_GROUP["student (ba)"],
        ],
        related_works=[
            PredicateObject(
                predicate=LOOKUP_DICT_RELATED_WORKS["isTranslationOf"],
                object="https://id.dalia.education/learning-resource/20be255e-e2da-4f9c-90b3-5573d6a12619",
            )
        ],
        file_size="703.2 MB",
        version=None,
    )
    graph = resource.get_graph()
    for k, v in CONVERTER.bimap.items():
        graph.bind(k, v)
    click.echo(graph.serialize(format="ttl"))


if __name__ == "__main__":
    _main()

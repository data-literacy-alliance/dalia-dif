"""Constants for DIF v1.3."""

import click

#: A single UUID to represent the resource under the ``dalia.oer`` prefix. Generate this UUID
#: yourself.
DIF_HEADER_ID = "DALIA_ID"
#: The SPDX license describing the upstream resource's terms and conditions. Dashes, spaces,
#: and capitalization are normalized.
#:
#: Warning: don't confuse this with the licensing of the metadata curated in the DIF, which
#: is licensed independently (we suggest CC0 for maximum reusability)
#:
#: This field also accepts the literal strings
#: ``proprietary`` or ``unlicensed``. For example, videos on YouTube are often licensed with
#: YouTube's proprietary license if the creator did not opt into using CC-BY-4.0.
DIF_HEADER_LICENSE = "License"
#: The URL link to the OER. Ideally, this is a DOI or other persistent identifier, but it can
#: be any URL that resolves
DIF_HEADER_LINK = "Link"
#: The language of the OER, written as an ISO two-letter code (e.g., `en` for English, `de`
#: for German)
DIF_HEADER_LANGUAGE = "Language"
#: The title of the resource. Please write this in the same language mentioned in the "Language"
#: column. If a colon `:` is present, the first one will be used to split the title into a title
#: and subtitle, which get put in different fields in DIF v1.3.
DIF_HEADER_TITLE = "Title"
#: A textual description of the resource. Please write this in the same language mentioned in the
#: "Language" column
DIF_HEADER_DESCRIPTION = "Description"
#: A list of authors, separated by asterisks. Each author should be written with family names, then
#: a comma, then given names. If an ORCID is available, then it can be added with a colon ``:``
#: then inside curly braces like in the following example.
#:
#: For example, `Kremer, Dominik : {https://orcid.org/0000-0003-1244-7363} * Geiger, Jonathan : {https://orcid.org/0000-0002-0452-7075}`
DIF_HEADER_AUTHORS = "Authors"
#: A list of UUIDs corresponding to pre-curated communities in DALIA. If you would like to request
#: a new one, please email charles.hoyt@ac.rwth-aachen.de.
DIF_HEADER_COMMUNITY = "Community"
#: The disciplines (e.g., chemistry, biology) covered by the resource encoded using
#: URIs from the DINI-KIM Hochschulfächersystematik resource, like
#: https://w3id.org/kim/hochschulfaechersystematik/n7.
#:
#: See https://w3id.org/kim/hcrt/scheme.html where you can search for the term and copy
#: the correct URI. When a discipline is missing from the resource, please either directly make an
#: issue on the upstream [GitHub repository](https://github.com/dini-ag-kim/hcrt) or email
#: charles.hoyt@ac.rwth-aachen.de for help
DIF_HEADER_DISCIPLINE = "Discipline"
#: A list of file extensions used by the resource (e.g., `.pdf`).
#: If multiple are available, please use an asterisk as a delimiter (e.g., `.pdf * .zip`).
DIF_HEADER_FILE_FORMAT = "FileFormat"
#: Free text keywords for the resource, delimited by an asterick (e.g.,
#: `digital humanities * culture`). Please write keywords in the same language
#: mentioned in the "Language" column
DIF_HEADER_KEYWORDS = "Keywords"
#: The learning resource type. Choose one of the keys in
#: :data:`dalia_dif.dif13.picklist.LEARNING_RESOURCE_TYPES`.
DIF_HEADER_LEARNING_RESOURCE_TYPE = "LearningResourceType"
#: The media type says what modality the learning resource has (e.g., audio, video, text).
#: This is a more broad category than learning resource type. Choose from
#: one of the keys in :data:`dalia_dif.dif13.picklist.MEDIA_TYPES`.
DIF_HEADER_MEDIA_TYPE = "MediaType"
#: One of the five proficiency levels described by the Dreyfus adaptive learning model
#: (https://doi.org/10.1177/02704676042649): novice, advanced beginner, competent, proficient, or
#: expert. These are encoded in :data:`dalia_dif.dif13.picklist.PROFICIENCY_LEVELS`
DIF_HEADER_PROFICIENCY_LEVEL = "ProficiencyLevel"
#: The date of publication, written in ISO standard format YYYY-MM-DD
DIF_HEADER_PUBLICATION_DATE = "PublicationDate"
#: The target audience (e.g., school students, bachelor's level students, data stewards, etc.).
#: Choose from the keys in :data:`dalia_dif.dif13.picklist.TARGET_GROUPS`.
DIF_HEADER_TARGET_GROUP = "TargetGroup"
#: Links to related works. These are curated as an asterisk-delimited list of predicate-value pairs
#: like: `isPartOf:https://doi.org/10.11588/heidicon/1738716` where the first part of the string is
#: a key from :data:`dalia_dif.dif13.picklist.RELATED_WORKS_RELATIONS` followed by a colon, then
#: the URL (ideally a DOI or other persistent identifier) to the target of the relation.
DIF_HEADER_RELATED_WORK = "RelatedWork"
#: The size, in megabytes (MB) of the file (e.g., `0.142`). Use a maximum of 3 places after the
#: decimal point. Do not write `MB`.
DIF_HEADER_SIZE = "Size"
#: The version of the OER. The same OER that is updated over time might have different versions,
#: each of which could be assigned their own record (and UUID) in DALIA.
DIF_HEADER_VERSION = "Version"

#: separator used for list fields
DIF_SEPARATOR = " * "

REQUIRED = {
    DIF_HEADER_ID,
    DIF_HEADER_LINK,
    DIF_HEADER_TITLE,
    DIF_HEADER_LANGUAGE,
    DIF_HEADER_LICENSE,
}


@click.command()
def main() -> None:
    """Create a curation guide based on this document."""
    import sys
    from pathlib import Path
    from textwrap import dedent

    from sphinx.pycode import ModuleAnalyzer

    module_root = Path(__file__).parent.parent.resolve()
    repo_root = module_root.parent.parent.resolve()

    path = repo_root.joinpath("docs", "curation.md")

    analyzer = ModuleAnalyzer.for_file(__file__, "mymodule")
    analyzer.analyze()

    text = dedent("""\
    # DALIA DIF v1.3 CSV Curation Guide

    This guide contains an explanation of the headers that can
    appear within a DIF v1.3 CSV file. Each has an explanation of what
    data type goes in each (string, URI reference, date, etc.), whether
    it's required or optional, and an explanation of how to curate values.

    ## Columns
    """)

    # Get the extracted documentation
    for (_, variable_name), docs_lines in analyzer.attr_docs.items():
        if variable_name.startswith("DIF_HEADER"):
            variable_value = getattr(sys.modules[__name__], variable_name)
            docs = "\n".join(docs_lines)
            required_text = " (required)" if variable_value in REQUIRED else ""
            column_text = f"""
### `{variable_value}`{required_text}

{docs}"""
            text += column_text

    text = text.rstrip()
    text += dedent(f"""

    ## Colophon

    Additional example files can be found in
    https://github.com/data-literacy-alliance/dalia-curation.

    This guide was autogenerated from the code documentation
    in `{Path(__file__).relative_to(repo_root)}`
    """)

    path.write_text(text)


if __name__ == "__main__":
    main()

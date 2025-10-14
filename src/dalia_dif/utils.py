"""Utilities."""

from pydantic_extra_types.language_code import ISO639_3, _index_by_alpha2
from tqdm import tqdm

__all__ = [
    "cleanup_languages",
]


def cleanup_languages(language_codes: str | list[str]) -> list[ISO639_3]:
    """Extract languages from a code string."""
    if isinstance(language_codes, str):
        language_codes = [language_codes]
    r = []
    for language_code in language_codes:
        if language_code == "N/A":
            continue
        if len(language_code) == 2:
            r.append(ISO639_3(_index_by_alpha2()[language_code].alpha3))
        elif len(language_code) == 3:
            r.append(ISO639_3(language_code))
        else:
            tqdm.write(f"can not handle language code: {language_code}")
    return r

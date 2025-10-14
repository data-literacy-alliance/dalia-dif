import pytest

from dalia_dif.dif13.legacy.authors import is_valid_wikidata_concept_uri


@pytest.mark.parametrize(
    "valid_wikidata_concept_uri",
    [
        "http://www.wikidata.org/entity/Q42",
        "http://www.wikidata.org/entity/Q96678459",
    ],
)
def test_is_valid_wikidata_concept_uri_with_valid_wikidata_concept_uri(valid_wikidata_concept_uri):
    assert is_valid_wikidata_concept_uri(valid_wikidata_concept_uri)


@pytest.mark.parametrize(
    "invalid_wikidata_concept_uri",
    [
        "https://www.wikidata.org/entity/Q42",
    ],
)
def test_is_valid_wikidata_concept_uri_with_invalid_wikidata_concept_uri(
    invalid_wikidata_concept_uri,
):
    assert not is_valid_wikidata_concept_uri(invalid_wikidata_concept_uri)

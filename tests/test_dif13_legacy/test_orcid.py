import pytest

from dalia_dif.dif13.legacy.authors import is_valid_orcid


@pytest.mark.parametrize(
    "valid_orcid",
    [
        "https://orcid.org/0000-0001-2345-6789",
        "https://orcid.org/0000-0002-1825-0097",
        "https://orcid.org/0000-0003-2125-060X",
        "http://orcid.org/0000-0003-2125-060X",
    ],
)
def test_is_valid_orcid_with_valid_orcid(valid_orcid):
    assert is_valid_orcid(valid_orcid)


@pytest.mark.parametrize(
    "invalid_orcid",
    [
        # regex not matching
        "https://orcid.org/0000-0002-1825-009x",
        "orcid.org/0000-0001-2345-6789",
        # wrong check digit
        "https://orcid.org/0000-0001-2345-678X",
        "https://orcid.org/0000-0002-1825-0098",
    ],
)
def test_is_valid_orcid_with_invalid_orcid(invalid_orcid):
    assert not is_valid_orcid(invalid_orcid)

import pytest

from dalia_dif.dif13.legacy.authors import is_valid_ror_id


@pytest.mark.parametrize(
    "valid_ror_id",
    [
        "https://ror.org/03yrm5c26",
        "https://ror.org/04xfq0f34",
        "https://ror.org/05n911h24",
        "https://ror.org/05qj6w324",
    ],
)
def test_is_valid_ror_id_with_valid_ror_id(valid_ror_id):
    assert is_valid_ror_id(valid_ror_id)


@pytest.mark.parametrize(
    "invalid_ror_id",
    [
        # regex not matching
        "http://ror.org/03yrm5c26",
        "https://ror.org/13yrm5c26",
        "https://ror.org/03Yrm5c26",
        # wrong checksum
        "https://ror.org/03yrm5c27",
    ],
)
def test_is_valid_ror_id_with_invalid_ror_id(invalid_ror_id):
    assert not is_valid_ror_id(invalid_ror_id)

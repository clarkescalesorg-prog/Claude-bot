from leads.google_places import _normalise_uk_phone


def test_leading_zero_becomes_e164():
    assert _normalise_uk_phone("01234 567890") == "+441234567890"


def test_country_code_without_plus_gets_plus():
    assert _normalise_uk_phone("44 1234 567890") == "+441234567890"


def test_already_e164_is_unchanged():
    assert _normalise_uk_phone("+44 1234 567890") == "+441234567890"

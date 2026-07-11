from outreach.messages import render


def test_render_step1_includes_business_and_first_name():
    body = render(1, "Acme Roofing Ltd.", "Manchester")
    assert "Hi Acme," in body
    assert "Acme Roofing Ltd." in body


def test_render_step2_includes_city():
    body = render(2, "Bolton Roofers", "Bolton")
    assert "Bolton" in body


def test_render_falls_back_to_your_area_when_no_city():
    body = render(2, "Bolton Roofers", "")
    assert "your area" in body


def test_render_strips_trailing_punctuation_from_first_name():
    body = render(1, "Smith, Roofing", "Leeds")
    assert "Hi Smith," in body


def test_render_defaults_to_there_when_no_business_name():
    body = render(1, "", "Leeds")
    assert "Hi there," in body

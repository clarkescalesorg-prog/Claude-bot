from leads.segmentation import _tier_for


def test_tier_hot_at_and_above_threshold():
    assert _tier_for(50) == "hot"
    assert _tier_for(120) == "hot"


def test_tier_warm_range():
    assert _tier_for(20) == "warm"
    assert _tier_for(49) == "warm"


def test_tier_cold_below_threshold():
    assert _tier_for(19) == "cold"
    assert _tier_for(0) == "cold"

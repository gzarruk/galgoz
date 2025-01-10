from galgoz.indicators.base import Indicator

def test_base_empty_indicator():
    indicator = Indicator(name="Test Indicator")
    assert indicator.name == "Test Indicator"
    assert indicator.data is None
    assert indicator.output is None
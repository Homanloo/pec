import pytest
from api.brain.properties import prop as api_prop
from vle.brain.properties import prop as vle_prop


@pytest.mark.parametrize("prop", [api_prop, vle_prop])
def test_cyclohexane_and_cyclohexene_are_distinct(prop):
    assert prop["cyclohexane"]["MW"] == pytest.approx(84.161)
    assert prop["cyclohexene"]["MW"] == pytest.approx(82.145)


def test_api_and_web_share_the_same_data():
    assert api_prop == vle_prop

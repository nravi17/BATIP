from batip.core.exceptions import BATIPError


def test_exception():

    err = BATIPError("BATIP")

    assert str(err) == "BATIP"
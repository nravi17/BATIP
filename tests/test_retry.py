from batip.utils.retry import retry


def test_retry_returns_value():

    @retry(max_attempts=3)
    def sample():
        return 100

    assert sample() == 100
import pytest

from tests.sample_data import create_sample_chain


@pytest.fixture
def option_chain():
    return create_sample_chain()
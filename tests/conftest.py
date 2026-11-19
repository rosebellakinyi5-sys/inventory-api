import copy
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import data  # noqa: E402
from app import app as flask_app  # noqa: E402

SEED = copy.deepcopy(data.inventory)


@pytest.fixture(autouse=True)
def reset_inventory():
    """Restore the mock database before every test."""
    data.inventory[:] = copy.deepcopy(SEED)


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    return flask_app.test_client()

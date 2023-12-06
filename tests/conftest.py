import os
from pathlib import Path

# Set up classy test directory - has to been done before import
PATH_TEST = Path("/tmp/classy_test/")
os.environ["CLASSY_DATA_DIR"] = str(PATH_TEST)

PATH_TEST.mkdir(exist_ok=True)

# Data required to run some tests
PATH_DATA = Path() / "tests/data"

import pytest  # noqa
import classy  # noqa


def pytest_configure():
    pytest.PATH_DATA = PATH_DATA
    pytest.PATH_TEST = PATH_TEST

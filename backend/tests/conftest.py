from __future__ import annotations

import os
import tempfile
from pathlib import Path

_TMP_DIR = Path(tempfile.mkdtemp(prefix="omnimind-test-"))
os.environ["OMNIMIND_DATABASE_URL"] = f"sqlite:///{_TMP_DIR / 'test.db'}"
os.environ["OMNIMIND_DATA_DIR"] = str(_TMP_DIR)

import pytest  # noqa: E402
from starlette.testclient import TestClient  # noqa: E402

from app.db import init_db  # noqa: E402
from app.main import app  # noqa: E402

init_db()


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c

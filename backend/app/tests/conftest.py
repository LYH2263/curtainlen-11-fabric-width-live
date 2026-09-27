import os
import tempfile

_tmp = tempfile.mkdtemp(prefix="curtainlen-test-")
os.environ["DATA_DIR"] = _tmp

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import seed


@pytest.fixture(scope="module")
def client():
    # 全新临时库并初始化种子数据
    db = os.path.join(_tmp, "app.db")
    if os.path.exists(db):
        os.remove(db)
    with TestClient(app) as c:
        yield c

import pytest
from fastapi.testclient import TestClient

import app.db as db
from app.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(db, "DB_PATH", db_path)
    with TestClient(app) as c:
        yield c


def test_fabric_width_same_in_list_detail_and_estimate(client):
    listing = client.get("/api/fabrics").json()["items"]
    list_row = next(x for x in listing if x["id"] == 1)
    detail = client.get("/api/fabrics/1").json()
    est = client.get("/api/estimate?window_id=1&fabric_id=1").json()
    assert detail["fabric_width"] == list_row["fabric_width"]
    assert est["fabric"]["fabric_width"] == list_row["fabric_width"]
    # 顶层 fabric_width 与 fabric 行同源
    assert est["fabric_width"] == est["fabric"]["fabric_width"]


def test_new_width_takes_effect_immediately_for_panels_and_meters(client):
    before = client.get("/api/estimate?window_id=1&fabric_id=1").json()
    # 3.0m 宽 × 2.0 褶倍 = 6.0m，门幅 1.4 → 5 幅；裁高 2.6+0.10+0.15=2.85
    assert before["panels"] == 5
    assert before["meters"] == 14.25
    assert before["fabric_width"] == 1.4

    r = client.put("/api/fabrics/1", json={"fabric_width": 2.0})
    assert r.status_code == 200
    assert r.json()["fabric_width"] == 2.0

    after = client.get("/api/estimate?window_id=1&fabric_id=1").json()
    # 6.0 / 2.0 = 3 幅；3 × 2.85 = 8.55m
    assert after["panels"] == 3
    assert after["meters"] == 8.55
    assert after["fabric_width"] == 2.0

    # 列表与下拉数据源同步读到新值
    listing = client.get("/api/fabrics").json()["items"]
    assert next(x for x in listing if x["id"] == 1)["fabric_width"] == 2.0


def test_non_positive_width_rejected_and_old_value_kept(client):
    for bad in (0, -1.4):
        r = client.put("/api/fabrics/2", json={"fabric_width": bad})
        assert r.status_code == 422
    r = client.put("/api/fabrics/2", json={"fabric_width": "abc"})
    assert r.status_code == 422
    # 库内旧值保留
    assert client.get("/api/fabrics/2").json()["fabric_width"] == 2.8


def test_history_run_keeps_snapshot_width_and_meters(client):
    saved = client.post("/api/estimate", json={"window_id": 1, "fabric_id": 1, "save": True}).json()
    run_id = saved["run_id"]
    assert saved["fabric_width"] == 1.4
    assert saved["meters"] == 14.25

    # 之后改门幅
    assert client.put("/api/fabrics/1", json={"fabric_width": 2.0}).status_code == 200

    runs = client.get("/api/runs").json()["items"]
    run = next(x for x in runs if x["id"] == run_id)
    # 历史编号仍显示写入时的门幅与米数，不被后来的门幅改写
    assert run["result"]["fabric_width"] == 1.4
    assert run["result"]["meters"] == 14.25
    assert run["result"]["panels"] == 5


def test_zero_width_fabric_estimate_is_422(client):
    # 种子布料 id=3 门幅为 0；服务层须拦截，而不是算出错误结果
    r = client.get("/api/estimate?window_id=1&fabric_id=3")
    assert r.status_code == 422


def test_update_missing_fabric_404(client):
    r = client.put("/api/fabrics/999", json={"fabric_width": 1.5})
    assert r.status_code == 404

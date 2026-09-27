import math

from app.repositories import fabrics as fabric_repo
from app.repositories import history as history_repo


def test_fabric_width_takes_effect_e2e(client):
    # 初始门幅 1.4m，客厅窗 3.0x2.6，褶倍 2，上下折边 0.10/0.15
    r = client.get("/api/estimate", params={"window_id": 1, "fabric_id": 1})
    assert r.status_code == 200
    first = r.json()
    assert first["fabric_width"] == 1.4
    assert first["panels"] == 5
    assert first["meters"] == 14.25

    # 布料列表读到的门幅与试算回包一致
    listed = next(f for f in client.get("/api/fabrics").json()["items"] if f["id"] == 1)
    assert listed["fabric_width"] == 1.4


def test_patch_width_then_recompute(client):
    # 保存新门幅 2.8m
    r = client.patch("/api/fabrics/1", json={"fabric_width": 2.8})
    assert r.status_code == 200
    assert r.json()["fabric_width"] == 2.8

    # 布料列表、算料台(重新拉列表)、测算回包三处读到同一值
    listed = next(f for f in client.get("/api/fabrics").json()["items"] if f["id"] == 1)
    assert listed["fabric_width"] == 2.8

    est = client.get("/api/estimate", params={"window_id": 1, "fabric_id": 1}).json()
    assert est["fabric"]["fabric_width"] == 2.8
    assert est["fabric_width"] == 2.8

    # panels 与 meters 按新门幅重算：成品宽 6.0 / 2.8 -> ceil 3 幅；3 * 2.85 = 8.55m
    assert est["panels"] == 3
    assert math.isclose(est["meters"], 8.55)


def test_non_positive_width_rejected_and_old_value_kept(client):
    for bad in (0, -1.4):
        r = client.patch("/api/fabrics/1", json={"fabric_width": bad})
        assert r.status_code == 422
    # 库内旧值保留
    assert fabric_repo.get_fabric(1)["fabric_width"] == 2.8

    # 非数字 / 空值由请求校验拦截
    r = client.patch("/api/fabrics/1", json={"fabric_width": "abc"})
    assert r.status_code == 422
    assert fabric_repo.get_fabric(1)["fabric_width"] == 2.8


def test_estimate_rejects_non_positive_width(client):
    # 种子脏数据布料 id=3 门幅为 0：测算必须返回 422 而不是 500
    r = client.get("/api/estimate", params={"window_id": 1, "fabric_id": 3})
    assert r.status_code == 422


def test_history_keeps_snapshot_after_width_changes(client):
    # 以当前 2.8m 门幅保存一条历史
    saved = client.post("/api/estimate", json={"window_id": 1, "fabric_id": 1, "save": True, "note": "2.8 时保存"})
    assert saved.status_code == 200
    run_id = saved.json()["run_id"]
    assert run_id

    # 后来改门幅为 1.4m
    r = client.patch("/api/fabrics/1", json={"fabric_width": 1.4})
    assert r.status_code == 200

    # 打开历史编号，仍显示写入时的门幅与米数
    runs = client.get("/api/runs").json()["items"]
    run = next(x for x in runs if x["id"] == run_id)
    assert run["result"]["fabric_width"] == 2.8
    assert run["result"]["panels"] == 3
    assert math.isclose(run["result"]["meters"], 8.55)

    # 仓储层快照一致，且不被后来的布料当前值影响
    repo_rows = history_repo.list_runs(50)
    repo_run = next(x for x in repo_rows if x["id"] == run_id)
    assert repo_run["result"]["fabric_width"] == 2.8
    assert fabric_repo.get_fabric(1)["fabric_width"] == 1.4

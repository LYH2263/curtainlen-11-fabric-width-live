from app.db import connect

def list_fabrics():
    c = connect()
    try:
        return [dict(r) for r in c.execute("SELECT * FROM fabrics ORDER BY id").fetchall()]
    finally:
        c.close()

def get_fabric(fid: int):
    c = connect()
    try:
        r = c.execute("SELECT * FROM fabrics WHERE id=?", (fid,)).fetchone()
        return dict(r) if r else None
    finally:
        c.close()

def update_fabric_width(fid: int, fabric_width: float):
    c = connect()
    try:
        cur = c.execute("UPDATE fabrics SET fabric_width=? WHERE id=?", (float(fabric_width), fid))
        c.commit()
        if cur.rowcount == 0:
            return None
        r = c.execute("SELECT * FROM fabrics WHERE id=?", (fid,)).fetchone()
        return dict(r) if r else None
    finally:
        c.close()

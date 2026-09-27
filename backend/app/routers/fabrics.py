from fastapi import APIRouter, HTTPException
from app.schemas.fabric import FabricWidthUpdate
from app.repositories import fabrics as repo
router = APIRouter()
@router.get("/fabrics")
def list_fabrics(): return {"items": repo.list_fabrics()}
@router.get("/fabrics/{fid}")
def get_fabric(fid: int):
    r = repo.get_fabric(fid)
    if not r: raise HTTPException(404)
    return r
@router.patch("/fabrics/{fid}")
def patch_fabric(fid: int, body: FabricWidthUpdate):
    if not repo.get_fabric(fid):
        raise HTTPException(404)
    if body.fabric_width != body.fabric_width or body.fabric_width <= 0:
        raise HTTPException(422, "门幅必须为正数")
    r = repo.update_fabric_width(fid, body.fabric_width)
    if not r:
        raise HTTPException(404)
    return r

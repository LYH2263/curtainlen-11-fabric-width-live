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
@router.put("/fabrics/{fid}")
def update_fabric(fid: int, body: FabricWidthUpdate):
    r = repo.update_width(fid, body.fabric_width)
    if not r: raise HTTPException(404, "fabric not found")
    return r

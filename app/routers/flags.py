from fastapi import APIRouter, Depends, HTTPException, Query
from google.cloud import firestore
from datetime import datetime, timezone
from ..deps import get_db, auth_dependency
from ..models import FlagIn, FlagOut

router = APIRouter()

def _doc_to_dict(doc):
    d = doc.to_dict() or {}
    d["id"] = doc.id
    for k in ("ts", "createdAt", "updatedAt"):
        v = d.get(k)
        try:
            if hasattr(v, "to_datetime"):
                d[k] = v.to_datetime().isoformat()
            elif hasattr(v, "isoformat"):
                d[k] = v.isoformat()
        except Exception:
            pass
    return d

@router.get("/", response_model=dict)
def list_flags(scope: str | None = Query(default=None),
               key: str | None = Query(default=None),
               limit: int = Query(default=20, ge=1, le=100),
               db: firestore.Client = Depends(get_db),
               _=Depends(auth_dependency)):
    q = db.collection("flags")
    if scope:
        q = q.where("scope","==", scope)
    if key:
        q = q.where("key","==", key)
    q = q.limit(limit)
    docs = q.stream()
    items = [_doc_to_dict(d) for d in docs]
    return {"items": items}

@router.post("/", response_model=FlagOut, status_code=201)
def create_flag(payload: FlagIn,
                db: firestore.Client = Depends(get_db),
                _=Depends(auth_dependency)):
    data = payload.model_dump()
    data["updatedAt"] = data.get("updatedAt") or datetime.now(timezone.utc)
    ref = db.collection("flags").add(data)[1]
    return _doc_to_dict(ref.get())

@router.get("/{doc_id}", response_model=FlagOut)
def get_flag(doc_id: str,
             db: firestore.Client = Depends(get_db),
             _=Depends(auth_dependency)):
    doc = db.collection("flags").document(doc_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="not_found")
    return _doc_to_dict(doc)

@router.put("/{doc_id}", response_model=FlagOut)
def update_flag(doc_id: str, patch: dict,
                db: firestore.Client = Depends(get_db),
                _=Depends(auth_dependency)):
    ref = db.collection("flags").document(doc_id)
    if not ref.get().exists:
        raise HTTPException(status_code=404, detail="not_found")
    ref.set(patch, merge=True)
    return _doc_to_dict(ref.get())

@router.delete("/{doc_id}", status_code=204)
def delete_flag(doc_id: str,
                db: firestore.Client = Depends(get_db),
                _=Depends(auth_dependency)):
    db.collection("flags").document(doc_id).delete()
    return

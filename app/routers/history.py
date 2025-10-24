from fastapi import APIRouter, Depends, HTTPException, Query
from google.cloud import firestore_v1 as firestore
from datetime import datetime, timezone
from ..deps import get_db, auth_dependency
from ..models import HistoryIn, HistoryOut

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
def list_history(userId: str | None = Query(default=None),
                 limit: int = Query(default=20, ge=1, le=100),
                 db: firestore.Client = Depends(get_db),
                 _=Depends(auth_dependency)):
    q = db.collection("history")
    
    # Estrategia: aplicar filtros pero NO ordenar para evitar índices complejos
    if userId:
        q = q.where("userId", "==", userId)
    
    # Obtener más documentos de los solicitados para poder ordenar en memoria
    fetch_limit = min(limit * 2, 100)  # Fetch el doble pero máximo 100
    q = q.limit(fetch_limit)
    
    docs = list(q.stream())
    
    # Ordenar en memoria por timestamp descendente si hay datos
    if docs:
        docs.sort(key=lambda doc: doc.to_dict().get("ts", datetime.min.replace(tzinfo=timezone.utc)), reverse=True)
    
    # Aplicar el límite final después del ordenamiento
    docs = docs[:limit]
    items = [_doc_to_dict(d) for d in docs]
    return {"items": items}

@router.post("/", response_model=HistoryOut, status_code=201)
def create_history(payload: HistoryIn,
                   db: firestore.Client = Depends(get_db),
                   _=Depends(auth_dependency)):
    data = payload.model_dump()
    data["ts"] = data.get("ts") or datetime.now(timezone.utc)
    ref = db.collection("history").add(data)[1]
    doc = ref.get()
    return _doc_to_dict(doc)

@router.get("/{doc_id}", response_model=HistoryOut)
def get_history(doc_id: str,
                db: firestore.Client = Depends(get_db),
                _=Depends(auth_dependency)):
    doc = db.collection("history").document(doc_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="not_found")
    return _doc_to_dict(doc)

@router.put("/{doc_id}", response_model=HistoryOut)
def update_history(doc_id: str, patch: dict,
                   db: firestore.Client = Depends(get_db),
                   _=Depends(auth_dependency)):
    ref = db.collection("history").document(doc_id)
    if not ref.get().exists:
        raise HTTPException(status_code=404, detail="not_found")
    ref.set(patch, merge=True)
    return _doc_to_dict(ref.get())

@router.delete("/{doc_id}", status_code=204)
def delete_history(doc_id: str,
                   db: firestore.Client = Depends(get_db),
                   _=Depends(auth_dependency)):
    db.collection("history").document(doc_id).delete()
    return

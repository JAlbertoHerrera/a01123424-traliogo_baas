from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
import os

from google.cloud import aiplatform
from vertexai import init as vertex_init
from vertexai.generative_models import GenerativeModel

from ..deps import get_db  # tu firestore (firebase-admin) inicializado en app/main.py

router = APIRouter(prefix="/api/v1/prompts", tags=["ai-prompts"])

PROJECT_ID = os.getenv("GCLOUD_PROJECT")
LOCATION = os.getenv("VERTEX_LOCATION", "us-central1")
MODEL_NAME = os.getenv("VERTEX_MODEL", "gemini-1.5-flash")

class PromptIn(BaseModel):
    prompt: str = Field(..., description="Texto a enviar al modelo")
    model: Optional[str] = Field(None, description="Override del modelo")

class PromptUpdate(BaseModel):
    note: Optional[str] = None

COL = "prompts"
def col(): return get_db().collection(COL)

def vertex():
    aiplatform.init(project=PROJECT_ID, location=LOCATION)
    vertex_init(project=PROJECT_ID, location=LOCATION)
    model = GenerativeModel(MODEL_NAME)
    return model

@router.post("", status_code=201)
def create_prompt(body: PromptIn):
    try:
        model = GenerativeModel(body.model or MODEL_NAME)
    except Exception:
        # init si hace falta
        aiplatform.init(project=PROJECT_ID, location=LOCATION)
        vertex_init(project=PROJECT_ID, location=LOCATION)
        model = GenerativeModel(body.model or MODEL_NAME)

    try:
        output = model.generate_content(body.prompt).text
    except Exception as e:
        raise HTTPException(400, f"VertexAI error: {e}")

    doc = {
        "prompt": body.prompt,
        "model": body.model or MODEL_NAME,
        "output": output,
        "ts": datetime.now(timezone.utc)
    }
    ref = col().add(doc)[1]  # (ref, write_result) -> usamos ref
    return {"id": ref.id, **doc}

@router.get("")
def list_prompts(limit: int = Query(10, ge=1, le=100)):
    try:
        snap = col().orderBy("ts", direction="DESCENDING").limit(limit).get()
        items = [ {"id": d.id, **d.to_dict()} for d in snap ]
        return {"items": items}
    except Exception as e:
        raise HTTPException(400, str(e))

@router.get("/{id}")
def get_prompt(id: str):
    d = col().document(id).get()
    if not d.exists: raise HTTPException(404, "not_found")
    return {"id": d.id, **d.to_dict()}

@router.put("/{id}")
def update_prompt(id: str, body: PromptUpdate):
    ref = col().document(id)
    if not ref.get().exists: raise HTTPException(404, "not_found")
    ref.set({k:v for k,v in body.dict().items() if v is not None}, merge=True)
    return {"id": id, **ref.get().to_dict()}

@router.delete("/{id}", status_code=204)
def delete_prompt(id: str):
    col().document(id).delete()

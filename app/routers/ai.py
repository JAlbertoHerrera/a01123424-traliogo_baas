from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from google.cloud import aiplatform
from vertexai import init as vertex_init
from vertexai.generative_models import GenerativeModel

from ..deps import get_db, auth_dependency  # tu firestore (firebase-admin) inicializado en app/main.py

load_dotenv()
router = APIRouter(prefix="/api/v1/prompts", tags=["ai-prompts"])

PROJECT_ID = os.getenv("GCLOUD_PROJECT")
LOCATION = os.getenv("VERTEX_LOCATION", "us-central1")
MODEL_NAME = os.getenv("VERTEX_MODEL", "")

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
def create_prompt(body: PromptIn, user=Depends(auth_dependency)):
    try:
        # Inicializar si es necesario
        aiplatform.init(project=PROJECT_ID, location=LOCATION)
        vertex_init(project=PROJECT_ID, location=LOCATION)
        
        model = GenerativeModel(body.model or MODEL_NAME)
        
        # Generar contenido con configuración económica
        response = model.generate_content(
            body.prompt,
            generation_config={
                'max_output_tokens': 500,  # Limitar tokens para ser económico
                'temperature': 0.7
            }
        )
        output = response.text
        
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg and "permission" in error_msg.lower():
            raise HTTPException(503, "Vertex AI permissions are still propagating. Please try again in a few minutes.")
        elif "quota" in error_msg.lower():
            raise HTTPException(429, "Vertex AI quota exceeded. Please try again later.")
        else:
            raise HTTPException(400, f"Vertex AI error: {error_msg}")

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
        snap = col().order_by("ts", direction="DESCENDING").limit(limit).get()
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
 
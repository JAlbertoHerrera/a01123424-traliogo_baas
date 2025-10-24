from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from google.cloud import secretmanager
import os

router = APIRouter(prefix="/api/v1/secrets", tags=["secrets"])

PROJECT_ID = os.getenv("GCLOUD_PROJECT")

class SecretCreate(BaseModel):
    key: str = Field(..., description="ID del secreto (único en el proyecto)")
    value: str = Field(..., description="Contenido de la versión inicial")
    labels: Optional[dict] = None

class SecretUpdate(BaseModel):
    value: str = Field(..., description="Nuevo valor (crea nueva versión)")

client = secretmanager.SecretManagerServiceClient()

def secret_name(key: str) -> str:
    return f"projects/{PROJECT_ID}/secrets/{key}"

@router.post("", status_code=201)
def create_secret(body: SecretCreate):
    parent = f"projects/{PROJECT_ID}"
    # Crea el secreto (metadata)
    try:
        client.create_secret(
            request={
                "parent": parent,
                "secret_id": body.key,
                "secret": {
                    "replication": {"automatic": {}},
                    "labels": body.labels or {}
                },
            }
        )
    except Exception as e:
        # Si ya existe, sigue (para poder crear versión); de lo contrario lanza error
        if "AlreadyExists" not in str(e):
            raise HTTPException(400, f"create_secret: {e}")

    # Crea la versión inicial
    try:
        client.add_secret_version(
            request={
                "parent": secret_name(body.key),
                "payload": {"data": body.value.encode("utf-8")}
            }
        )
    except Exception as e:
        raise HTTPException(400, f"add_secret_version: {e}")

    return {"id": body.key, "labels": body.labels or {}}

@router.get("")
def list_secrets(prefix: Optional[str] = Query(None, description="Filtra por prefijo")):
    parent = f"projects/{PROJECT_ID}"
    items = []
    for s in client.list_secrets(request={"parent": parent}):
        sid = s.name.split("/")[-1]
        if prefix and not sid.startswith(prefix):
            continue
        items.append({"id": sid, "labels": dict(s.labels)})
    return {"items": items}

@router.get("/{key}")
def get_secret_latest(key: str):
    name = f"{secret_name(key)}/versions/latest"
    try:
        resp = client.access_secret_version(request={"name": name})
        value = resp.payload.data.decode("utf-8")
        return {"id": key, "value": value}
    except Exception as e:
        raise HTTPException(404, f"access_secret_version: {e}")

@router.put("/{key}")
def update_secret_add_version(key: str, body: SecretUpdate):
    # En Secret Manager, “update” se modela como crear una nueva versión
    try:
        client.add_secret_version(
            request={
                "parent": secret_name(key),
                "payload": {"data": body.value.encode("utf-8")}
            }
        )
        return {"id": key, "updated": True}
    except Exception as e:
        raise HTTPException(400, f"add_secret_version: {e}")

@router.delete("/{key}", status_code=204)
def delete_secret(key: str):
    try:
        client.delete_secret(request={"name": secret_name(key)})
    except Exception as e:
        raise HTTPException(400, f"delete_secret: {e}")

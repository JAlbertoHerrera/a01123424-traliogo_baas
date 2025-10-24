import os
from fastapi import Depends, HTTPException, status
from google.cloud import firestore
import firebase_admin
from firebase_admin import auth as fb_auth

_db = None

def get_db():
    global _db
    if _db is None:
        project = os.getenv("GCLOUD_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT")
        _db = firestore.Client(project=project) if project else firestore.Client()
    return _db

REQUIRE_AUTH = os.getenv("REQUIRE_AUTH", "false").lower() == "true"

def verify_bearer(token: str | None):
    if not REQUIRE_AUTH:
        return None
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    try:
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        decoded = fb_auth.verify_id_token(token)
        return decoded
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def auth_dependency(authorization: str | None = None):
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
    return verify_bearer(token)

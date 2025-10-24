import os
from fastapi import Depends, HTTPException, status, Header
from google.cloud import firestore
import firebase_admin
from firebase_admin import auth as fb_auth

_db = None

def get_db():
    global _db
    if _db is None:
        from firebase_admin import credentials
        import firebase_admin
        
        # Inicializar Firebase Admin si no está inicializado
        if not firebase_admin._apps:
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if credentials_path and os.path.exists(credentials_path):
                cred = credentials.Certificate(credentials_path)
                firebase_admin.initialize_app(cred)
            else:
                firebase_admin.initialize_app()
        
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
            from firebase_admin import credentials
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            
            if credentials_path and os.path.exists(credentials_path):
                cred = credentials.Certificate(credentials_path)
                firebase_admin.initialize_app(cred)
            else:
                firebase_admin.initialize_app()
        
        # Para desarrollo: aceptar custom tokens directamente
        # En producción esto debería verificar ID tokens reales
        if token.startswith('eyJ'):  # Es un JWT
            return {"uid": "test-user-123"}  # Mock para desarrollo
        else:
            raise Exception("Invalid token format")
            
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}")

def auth_dependency(authorization: str | None = Header(None)):
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
    return verify_bearer(token)
 
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import firebase_admin
from firebase_admin import auth, credentials
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

class LoginRequest(BaseModel):
    user_id: str = "test-user-123"
    email: Optional[str] = "test@trailogo.com"

class TokenResponse(BaseModel):
    token: str
    expires_in: int
    user_id: str

@router.post("/auth/token", response_model=TokenResponse, tags=["auth"])
async def generate_test_token(request: LoginRequest):
    """
    Genera un token de Firebase para testing automático.
    Este endpoint está diseñado para facilitar las pruebas con Postman.
    """
    try:
        # Inicializar Firebase Admin si no está inicializado
        if not firebase_admin._apps:
            project_id = os.getenv('GCLOUD_PROJECT', 'trailogo-dev')
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            
            if credentials_path:
                # Normalizar ruta para Windows
                credentials_path = os.path.normpath(credentials_path)
                
                if os.path.exists(credentials_path):
                    cred = credentials.Certificate(credentials_path)
                    firebase_admin.initialize_app(cred, options={'projectId': project_id})
                else:
                    raise Exception(f"Archivo de credenciales no encontrado: {credentials_path}")
            else:
                raise Exception("GOOGLE_APPLICATION_CREDENTIALS no está configurado")
        
        # Crear custom token (sin claims por simplicidad)
        custom_token = auth.create_custom_token(request.user_id)
        
        return TokenResponse(
            token=custom_token.decode('utf-8'),
            expires_in=3600,  # 1 hora
            user_id=request.user_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando token: {str(e)}"
        )

@router.get("/auth/health", tags=["auth"])
async def auth_health():
    """
    Verifica que Firebase Admin esté configurado correctamente
    """
    try:
        if not firebase_admin._apps:
            project_id = os.getenv('GCLOUD_PROJECT', 'trailogo-dev')
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            
            if credentials_path:
                # Normalizar ruta para Windows
                credentials_path = os.path.normpath(credentials_path)
                
                if os.path.exists(credentials_path):
                    cred = credentials.Certificate(credentials_path)
                    firebase_admin.initialize_app(cred, options={'projectId': project_id})
                else:
                    raise Exception(f"Archivo de credenciales no encontrado: {credentials_path}")
            else:
                raise Exception("GOOGLE_APPLICATION_CREDENTIALS no está configurado")
        
        # Intentar crear un token de prueba
        test_token = auth.create_custom_token("health-check")
        
        return {
            "status": "ok",
            "firebase_admin": "initialized",
            "can_generate_tokens": True
        }
        
    except Exception as e:
        return {
            "status": "error",
            "firebase_admin": "error",
            "can_generate_tokens": False,
            "error": str(e)
        }
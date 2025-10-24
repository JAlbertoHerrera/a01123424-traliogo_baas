#!/usr/bin/env python3
"""
Script para obtener Firebase ID Token para testing
Requiere: pip install firebase-admin
"""

import firebase_admin
from firebase_admin import auth, credentials
import sys
import os

def get_custom_token(project_id: str, user_id: str = "test-user-123"):
    """
    Genera un custom token para el usuario especificado
    """
    try:
        # Inicializar Firebase Admin (usa Application Default Credentials)
        if not firebase_admin._apps:
            cred = credentials.Certificate("firebase-service-account.json")
            firebase_admin.initialize_app(cred)
        
        # Crear custom token
        custom_token = auth.create_custom_token(user_id)
        
        print(f"Custom token generado para usuario: {user_id}")
        print(f"Token: {custom_token.decode('utf-8')}")
        print("\nPara usar en Postman:")
        print(f"   Variable: idToken")
        print(f"   Valor: {custom_token.decode('utf-8')}")
        
        return custom_token.decode('utf-8')
        
    except Exception as e:
        print(f"Error generando token: {e}")
        return None

def main():
    project_id = os.getenv('GCLOUD_PROJECT', 'trailogo-dev')
    user_id = sys.argv[1] if len(sys.argv) > 1 else "test-user-123"
    
    print(f"Generando token para proyecto: {project_id}")
    print(f"Usuario: {user_id}")
    print("-" * 50)
    
    token = get_custom_token(project_id, user_id)
    
    if token:
        print("\nToken generado exitosamente!")
        print("Úsalo en el header: Authorization: Bearer <token>")
    else:
        print("\nNo se pudo generar el token")
        print("Asegúrate de tener permisos de Firebase Admin")

if __name__ == "__main__":
    main()
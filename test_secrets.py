import os
from google.cloud import secretmanager

def main():
    project_id = os.getenv("GCLOUD_PROJECT", "trailogo-dev")
    secret_id = "traliogo-test-secret"
    secret_value = "mi-secreto-super-seguro-123"
    
    print(f"Probando Secret Manager...")
    print(f"   Project: {project_id}")
    print(f"   Secret ID: {secret_id}")
    
    client = secretmanager.SecretManagerServiceClient()
    parent = f"projects/{project_id}"
    secret_path = f"{parent}/secrets/{secret_id}"
    
    try:
        # 1. Crear secreto
        print("1. Creando secreto...")
        try:
            client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": secret_id,
                    "secret": {
                        "replication": {"automatic": {}},
                        "labels": {"env": "test", "app": "traliogo"}
                    },
                }
            )
            print("Secreto creado")
        except Exception as e:
            if "AlreadyExists" in str(e):
                print("Secreto ya existe, continuando...")
            else:
                raise e
        
        # 2. Agregar versión con el valor
        print("2. Agregando versión del secreto...")
        client.add_secret_version(
            request={
                "parent": secret_path,
                "payload": {"data": secret_value.encode("utf-8")}
            }
        )
        print("Versión agregada")
        
        # 3. Listar secretos
        print("3. Listando secretos...")
        secrets = list(client.list_secrets(request={"parent": parent}))
        print(f"Encontrados {len(secrets)} secretos:")
        for secret in secrets[:5]:  # Solo mostrar primeros 5
            secret_name = secret.name.split("/")[-1]
            print(f"   - {secret_name} (labels: {dict(secret.labels)})")
        
        # 4. Obtener valor del secreto
        print("4. Obteniendo valor del secreto...")
        version_path = f"{secret_path}/versions/latest"
        response = client.access_secret_version(request={"name": version_path})
        retrieved_value = response.payload.data.decode("utf-8")
        print(f"Valor recuperado: {retrieved_value}")
        
        # 5. Verificar que el valor es correcto
        if retrieved_value == secret_value:
            print("El valor recuperado coincide con el original")
        else:
            print("El valor no coincide")
        
        # 6. Limpiar - eliminar secreto de prueba
        print("5. Limpiando secreto de prueba...")
        client.delete_secret(request={"name": secret_path})
        print("Secreto eliminado")
        
        print("Secret Manager funciona correctamente!")
        
    except Exception as e:
        print(f"Error: {e}")
        if "API has not been used" in str(e):
            print("Necesitas habilitar Secret Manager API:")
            print("   gcloud services enable secretmanager.googleapis.com")
        elif "permission" in str(e).lower():
            print("Verifica permisos de autenticación")
        elif "quota" in str(e).lower():
            print("Límite de cuota alcanzado")

if __name__ == "__main__":
    main()
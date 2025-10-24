import os
from google.cloud import aiplatform
from vertexai import init as vertex_init
from vertexai.generative_models import GenerativeModel

def main():
    project_id = os.getenv("GCLOUD_PROJECT", "trailogo-dev")
    location = os.getenv("VERTEX_LOCATION", "us-central1")
    model_name = os.getenv("VERTEX_MODEL", "gemini-1.5-flash")
    
    print(f"Probando Vertex AI...")
    print(f"   Project: {project_id}")
    print(f"   Location: {location}")
    print(f"   Model: {model_name}")
    
    try:
        # Inicializar Vertex AI
        aiplatform.init(project=project_id, location=location)
        vertex_init(project=project_id, location=location)
        print("Vertex AI inicializado")
        
        # Crear modelo
        model = GenerativeModel(model_name)
        print(f"Modelo {model_name} cargado")
        
        # Generar contenido
        prompt = "¿Qué es TralioGo y para qué sirve una app de traducción?"
        print(f"Enviando prompt: {prompt}")
        
        response = model.generate_content(prompt)
        output = response.text
        
        print("Respuesta del modelo:")
        print(f"   {output[:200]}{'...' if len(output) > 200 else ''}")
        print(f"Vertex AI funciona correctamente!")
        
    except Exception as e:
        print(f"Error: {e}")
        if "API has not been used" in str(e):
            print("Necesitas habilitar Vertex AI API:")
            print("   gcloud services enable aiplatform.googleapis.com")
        elif "quota" in str(e).lower():
            print("Límite de cuota alcanzado, intenta más tarde")
        elif "permission" in str(e).lower():
            print("Verifica permisos de autenticación")

if __name__ == "__main__":
    main()
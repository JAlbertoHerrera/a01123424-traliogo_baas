# TralioGo Backend API

Backend REST API para aplicación de traducción y aprendizaje de idiomas construido con Python, FastAPI y Google Cloud Platform.

## Características

- **API REST completa** con FastAPI
- **Base de datos** Firestore (NoSQL)
- **Almacenamiento** Google Cloud Storage  
- **Gestión de secretos** Secret Manager
- **IA Generativa** Vertex AI / Gemini
- **Autenticación** Firebase ID Tokens (opcional)
- **Documentación automática** Swagger UI
- **Deploy ready** Google Cloud Run

## Requisitos

- Python 3.11+
- Proyecto Google Cloud Platform
- Firestore en modo Native
- Google Cloud CLI configurado

## Configuración inicial

### 1. Clonar y instalar dependencias

```bash
git clone <repository-url>
cd TralioGo-Backend
pip install -r requirements.txt
```

### 2. Configurar Google Cloud

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```

### 3. Habilitar APIs necesarias

```bash
gcloud services enable firestore.googleapis.com
gcloud services enable storage-api.googleapis.com  
gcloud services enable secretmanager.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

### 4. Configurar variables de entorno

Copia `.env.example` a `.env` y ajusta los valores:

```bash
cp .env.example .env
```

Edita `.env`:
```env
# Autenticación
REQUIRE_AUTH=false

# Google Cloud Platform  
GCLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_PROJECT=your-project-id

# Vertex AI / Gemini
VERTEX_LOCATION=us-central1
VERTEX_MODEL=gemini-1.5-flash

# Aplicación
PORT=8080
HOST=0.0.0.0

# Desarrollo
DEBUG=true
```

## Ejecución local

```bash
uvicorn app.main:app --reload --port 8080
```

La aplicación estará disponible en:
- **API**: http://localhost:8080
- **Health check**: http://localhost:8080/healthz  
- **Documentación**: http://localhost:8080/docs

## Endpoints principales

### Core API
- `GET /api/v1/users/` - Listar usuarios
- `POST /api/v1/users/` - Crear usuario
- `GET /api/v1/users/{id}` - Obtener usuario
- `PUT /api/v1/users/{id}` - Actualizar usuario
- `DELETE /api/v1/users/{id}` - Eliminar usuario

### Historial de traducciones
- `GET /api/v1/history/` - Listar historial (filtrable por userId)
- `POST /api/v1/history/` - Crear registro
- `GET /api/v1/history/{id}` - Obtener registro
- `PUT /api/v1/history/{id}` - Actualizar registro
- `DELETE /api/v1/history/{id}` - Eliminar registro

### Objetos detectados
- `GET /api/v1/objects/` - Listar objetos (filtrable por createdBy)
- `POST /api/v1/objects/` - Crear objeto
- `GET /api/v1/objects/{id}` - Obtener objeto
- `PUT /api/v1/objects/{id}` - Actualizar objeto
- `DELETE /api/v1/objects/{id}` - Eliminar objeto

### Feature flags  
- `GET /api/v1/flags/` - Listar flags (filtrable por scope/key)
- `POST /api/v1/flags/` - Crear flag
- `GET /api/v1/flags/{id}` - Obtener flag
- `PUT /api/v1/flags/{id}` - Actualizar flag
- `DELETE /api/v1/flags/{id}` - Eliminar flag

### Gestión de secretos
- `GET /api/v1/secrets/` - Listar secretos
- `POST /api/v1/secrets/` - Crear secreto
- `GET /api/v1/secrets/{key}` - Obtener valor
- `PUT /api/v1/secrets/{key}` - Actualizar valor
- `DELETE /api/v1/secrets/{key}` - Eliminar secreto

### IA y prompts
- `GET /api/v1/prompts/` - Listar prompts ejecutados
- `POST /api/v1/prompts/` - Ejecutar prompt con Vertex AI
- `GET /api/v1/prompts/{id}` - Obtener prompt
- `PUT /api/v1/prompts/{id}` - Actualizar metadatos
- `DELETE /api/v1/prompts/{id}` - Eliminar prompt

## Autenticación

Por defecto la autenticación está deshabilitada. Para habilitarla:

1. Configurar `REQUIRE_AUTH=true` en `.env`
2. Enviar header `Authorization: Bearer <Firebase_ID_Token>` en requests

## Ingesta de datos

### Desde archivos JSON

```bash
cd ingesta
python ingestar_firestore.py --collection users --file users.json
python ingestar_firestore.py --collection history --file history.json  
python ingestar_firestore.py --collection objects --file objects.json
python ingestar_firestore.py --collection flags --file flags.json
```

### Generar datos sintéticos

```bash
python ingestar_firestore.py --collection users --generate 50
python ingestar_firestore.py --collection history --generate 100
```

### Modo dry-run

```bash
python ingestar_firestore.py --collection users --file users.json --dry-run
```

## Testing

### Scripts de prueba servicios individuales, valida que los servicios están disponibles

```bash
python test_firestore.py    # Conectividad Firestore
python test_storage.py      # Google Cloud Storage  
python test_secrets.py      # Secret Manager
python test_vertex.py       # Vertex AI / Gemini
```

## Colección de Postman

### Uso con autenticación automática

La colección `TralioGo_Postman_Collection.json` incluye autenticación automática con Firebase ID Tokens:

#### Características

- **Token automático**: Genera tokens Firebase automáticamente
- **Auto-renovación**: Los tokens se renuevan antes de expirar
- **CRUD completo**: Endpoints para Users, History, Objects, Flags
- **Tests incluidos**: Validación automática de respuestas

#### Variables configuradas

- `baseUrl`: Endpoint de la API (por defecto: `http://localhost:8080/api/v1`)
- `idToken`: Token Firebase (se maneja automáticamente)
- `lastId`: ID del último documento creado
- `tokenExpiry`: Timestamp de expiración del token

#### Cómo usar

1. **Importar colección** en Postman
2. **Configurar environment** (opcional):
   ```
   baseUrl: http://localhost:8080/api/v1
   ```
3. **Ejecutar autenticación**:
   - Ejecuta `AUTH > GET TOKEN (Auto)` una vez
4. **Usar endpoints**:
   - Todos los demás requests funcionarán automáticamente
   - El token se renueva automáticamente cuando sea necesario

#### Flujo recomendado

Para cada recurso (Users, History, Objects, Flags):
```
LIST → CREATE → GET → UPDATE → DELETE
```

#### Requisitos

- API ejecutándose en `http://localhost:8080`
- Autenticación habilitada (`REQUIRE_AUTH=true`)
- Firebase Admin configurado
- Dependencia: `pip install firebase-admin`

### Testing sin Postman

Si prefieres usar scripts Python directamente:

```bash
cd clientes
python cliente_users.py     # Prueba CRUD usuarios
python cliente_history.py   # Prueba CRUD historial
python cliente_objects.py   # Prueba CRUD objetos
python cliente_flags.py     # Prueba CRUD flags
python cliente_secrets.py   # Prueba gestión secretos
python cliente_prompts.py   # Prueba IA/prompts
```

## Deploy a Google Cloud Run (Esto no aplica de momento, no para este entregable)

### 1. Build y push imagen

```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/traliogo-api

# O con Docker
docker build -t gcr.io/YOUR_PROJECT_ID/traliogo-api .
docker push gcr.io/YOUR_PROJECT_ID/traliogo-api
```

### 2. Deploy servicio

```bash
gcloud run deploy traliogo-api \
  --image gcr.io/YOUR_PROJECT_ID/traliogo-api \
  --platform managed \
  --region us-central1 \
  --set-env-vars REQUIRE_AUTH=true,GCLOUD_PROJECT=YOUR_PROJECT_ID \
  --allow-unauthenticated
```

## Estructura del proyecto

```
.
├── app/
│   ├── main.py              # Aplicación FastAPI principal
│   ├── deps.py              # Dependencias (DB, auth)
│   ├── models.py            # Modelos Pydantic
│   └── routers/             # Endpoints organizados
│       ├── users.py
│       ├── history.py  
│       ├── objects.py
│       ├── flags.py
│       ├── secrets.py
│       └── ai.py
├── ingesta/                 # Scripts de ingesta de datos
│   ├── ingestar_firestore.py
│   ├── users.json
│   ├── history.json
│   ├── objects.json
│   └── flags.json
├── clientes/                # Scripts de prueba de endpoints
├── test_*.py                # Tests de conectividad servicios
├── .env.example             # Template variables de entorno
├── requirements.txt         # Dependencias Python
├── Dockerfile              # Imagen Docker
└── firestore.indexes.json  # Configuración índices Firestore
```

## Desarrollo

### Agregar nuevos endpoints

1. Crear router en `app/routers/`
2. Definir modelos en `app/models.py`  
3. Registrar router en `app/main.py`
4. Crear tests en `clientes/`

### Variables de entorno disponibles

Ver `.env.example` para lista completa de variables configurables.

### Logs y debugging

- Logs de aplicación en stdout
- FastAPI debug mode con `DEBUG=true`
- Swagger UI disponible en `/docs`

## Troubleshooting

### Error "API has not been used"
```bash
gcloud services enable <api-name>.googleapis.com
```

### Error "The query requires an index"
Usar las URLs proporcionadas en logs de error o configurar `firestore.indexes.json`

### Error de autenticación
```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```
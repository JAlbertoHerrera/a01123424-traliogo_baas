from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from .routers.history import router as history_router
from .routers.users import router as users_router
from .routers.objects import router as objects_router
from .routers.flags import router as flags_router
from .routers.secrets import router as secrets_router
from .routers.ai import router as prompts_router
from .routers.auth import router as auth_router
app = FastAPI(title="TralioGo API", version="1.0.0")

@app.get("/healthz", response_class=PlainTextResponse)
def healthz():
    return "ok"

app.include_router(history_router, prefix="/api/v1/history", tags=["history"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(objects_router, prefix="/api/v1/objects", tags=["objects"])
app.include_router(flags_router, prefix="/api/v1/flags", tags=["flags"])
app.include_router(secrets_router)
app.include_router(prompts_router)
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
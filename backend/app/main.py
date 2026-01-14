from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api import auth, user, sessions

settings = get_settings()

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(user.router, prefix="/api/user", tags=["user"])
app.include_router(sessions.router, prefix="/api", tags=["sessions"])


@app.get("/")
async def root():
    return {"message": "Login Demo API", "version": settings.APP_VERSION}


@app.get("/health")
async def health():
    return {"status": "healthy"}

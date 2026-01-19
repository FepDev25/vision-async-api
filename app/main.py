from fastapi import FastAPI
from app.core.config import settings
from app.routers import vision

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"   
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Incluir los routers
app.include_router(vision.router, prefix=settings.API_V1_STR)
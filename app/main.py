from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router

app = FastAPI(title="OpenAI Chess MVP")

app.include_router(api_router, prefix="/api")

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")

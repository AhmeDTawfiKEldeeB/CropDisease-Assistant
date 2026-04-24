from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import health, chat

app = FastAPI(title="CropDisease Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.routers import news, chat
from backend.scheduler import start_scheduler
from backend.database.db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    start_scheduler()
    yield
    # Shutdown (cleanup if needed)

app = FastAPI(
    title="AI News Aggregator",
    description="LLM + RAG powered news aggregation and Q&A API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news.router, prefix="/news", tags=["News"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])

@app.get("/")
async def root():
    return {"message": "AI News Aggregator API is running 🚀"}

@app.get("/health")
async def health():
    return {"status": "ok"}

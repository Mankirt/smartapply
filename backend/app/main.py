import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config.database import lifespan
from app.routes import resume, analyze, history


logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title = "SmartApply API",
    description = 'AI-Powered resume and JD fit analyzer',
    version = '1.0.0',
    lifespan = lifespan
)

#CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins = ['http://localhost:5173'],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ['*']
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter()  - start) * 1000
    logger.info(
        f"{request.method} {request.url.path} "
        f"-> {response.status_code}"
        f"[{duration_ms:.1f}]"
    )
    return response

app.include_router(resume.router, prefix="/api/resume", tags=["resume"])
app.include_router(analyze.router, prefix="/api/analyze", tags=["analyze"])
app.include_router(history.router, prefix="/api/history", tags=["history"])

@app.get('/health')
async def health_check():
    return {
        "status": 'ok',
        "version": '1.0.0'
    }

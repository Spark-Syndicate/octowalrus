from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.settings import settings
from core.logging import setup_logging, get_logger
from routes import api_router

setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="octowalrus",
    description="A fastapi service for octowalrus by Spark Syndicate",
    version="0.1.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)

logger.info("FastAPI application initialized")

app.add_middleware(
    CORSMiddleware,  # type: ignore[arg-type]
    allow_origins=settings.cors_allow_urls_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routes
app.include_router(api_router)

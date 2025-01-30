import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database import init_db
from app.routers import router

# Configure logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def get_application():
    # Initialize FastAPI application
    _app = FastAPI(title=settings.PROJECT_NAME,
                   version=settings.PROJECT_VERSION,
                   description=settings.PROJECT_DESCRIPTION,
                   summary=settings.PROJECT_SUMMARY,
                   contact={
                       "name": "Waqar Ali",
                       "email": "waqar.ali141@gmail.com",
                   },
                   )

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return _app


app = get_application()


# Initialize database on startup
@app.on_event("startup")
async def on_startup():
    await init_db()


# Include routers
app.include_router(router, prefix="/api/v1")

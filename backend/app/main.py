"""
Main FastAPI application entry point.
Follows SOLID principles with clear separation of concerns.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import logging

from .core.config import get_settings
from .api.v1.router import api_router
from .shared.exceptions.domain import DomainException
from .infrastructure.database.connection import init_database, close_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting up application...")
    await init_database()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await close_database()
    logger.info("Database connections closed")


def create_application() -> FastAPI:
    """
    Application factory.
    Creates and configures the FastAPI application.
    """
    app = FastAPI(
        title=settings.app.app_name,
        version=settings.app.app_version,
        debug=settings.app.debug,
        docs_url="/docs" if settings.app.debug else None,
        redoc_url="/redoc" if settings.app.debug else None,
        openapi_url="/openapi.json" if settings.app.debug else None,
        lifespan=lifespan
    )
    
    # Add middlewares
    setup_middlewares(app)
    
    # Add exception handlers
    setup_exception_handlers(app)
    
    # Include routers
    app.include_router(
        api_router,
        prefix=settings.app.api_v1_prefix
    )
    
    # Add health check endpoint
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "service": settings.app.app_name,
            "version": settings.app.app_version
        }
    
    return app


def setup_middlewares(app: FastAPI) -> None:
    """
    Configure application middlewares.
    Follows the Chain of Responsibility pattern.
    """
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.cors_origins,
        allow_credentials=settings.cors.cors_allow_credentials,
        allow_methods=settings.cors.cors_allow_methods,
        allow_headers=settings.cors.cors_allow_headers,
    )
    
    # Trusted host middleware (security)
    if settings.app.environment == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*.coisasdegaragem.com", "coisasdegaragem.com"]
        )


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Configure global exception handlers.
    Centralizes error handling logic.
    """
    
    @app.exception_handler(DomainException)
    async def domain_exception_handler(request, exc: DomainException):
        """Handle domain exceptions"""
        return JSONResponse(
            status_code=400,
            content={
                "error": exc.code,
                "message": exc.message
            }
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request, exc: ValueError):
        """Handle value errors"""
        return JSONResponse(
            status_code=400,
            content={
                "error": "VALUE_ERROR",
                "message": str(exc)
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        """Handle unexpected exceptions"""
        logger.error(f"Unexpected error: {exc}", exc_info=True)
        
        if settings.app.debug:
            return JSONResponse(
                status_code=500,
                content={
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": str(exc)
                }
            )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred"
            }
        )


# Create application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.reload,
        log_level=settings.logging.log_level.lower()
    )
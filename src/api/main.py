"""
recipe assistant fastapi application
main application entry point with complete setup
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path

#add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config.settings import get_settings
from src.api.middleware import setup_middleware, setup_exception_handlers, limiter
from src.api.routes.users import router as auth_router, user_router
from src.api.routes.recipes import router as recipe_router
from src.api.routes.ratings import router as rating_router
from src.api.routes.meal_plans import router as meal_plan_router
from src.api.routes.shopping_lists import router as shopping_list_router
from src.api.routes.nutrition import router as nutrition_router
from src.api.routes.substitutions import router as substitution_router
from src.api.routes.recommendations import router as recommendation_router
from src.database import get_db

#get settings
settings = get_settings()

#configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(settings.LOG_FILE)
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    lifespan context manager for startup and shutdown events
    """
    #startup
    logger.info(f"starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"environment: {settings.ENVIRONMENT}")
    logger.info(f"debug mode: {settings.DEBUG}")
    
    #ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    #initialize database
    try:
        db = get_db(settings.DATABASE_URL)
        stats = db.get_stats()
        logger.info(f"database initialized: {stats}")
    except Exception as e:
        logger.error(f"failed to initialize database: {e}")
        raise
    
    logger.info("application startup complete")
    
    yield
    
    #shutdown
    logger.info("shutting down application...")
    
    #close database connections
    try:
        db = get_db(settings.DATABASE_URL)
        db.close()
        logger.info("database connections closed")
    except Exception as e:
        logger.error(f"error closing database: {e}")
    
    logger.info("application shutdown complete")


#create fastapi application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="a comprehensive recipe management system with ai-powered features",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
    lifespan=lifespan
)

#add rate limiter state
app.state.limiter = limiter

#setup middleware
setup_middleware(app)
setup_exception_handlers(app)

#include routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(user_router, prefix=settings.API_V1_PREFIX)
app.include_router(recipe_router, prefix=settings.API_V1_PREFIX)
app.include_router(rating_router, prefix=settings.API_V1_PREFIX)
app.include_router(meal_plan_router, prefix=settings.API_V1_PREFIX)
app.include_router(shopping_list_router, prefix=settings.API_V1_PREFIX)
app.include_router(nutrition_router, prefix=settings.API_V1_PREFIX)
app.include_router(substitution_router, prefix=settings.API_V1_PREFIX)
app.include_router(recommendation_router, prefix=settings.API_V1_PREFIX)

#root endpoint
@app.get("/", tags=["root"])
async def root():
    """root endpoint - api information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if not settings.is_production else "disabled",
    }


#health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """health check endpoint"""
    try:
        #check database connection
        db = get_db(settings.DATABASE_URL)
        stats = db.get_stats()
        
        return {
            "status": "healthy",
            "database": "connected",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


#database stats endpoint (protected in production)
@app.get("/stats", tags=["admin"])
async def get_stats():
    """get database statistics"""
    if settings.is_production:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "not available in production"}
        )
    
    try:
        db = get_db(settings.DATABASE_URL)
        stats = db.get_stats()
        return stats
    except Exception as e:
        logger.error(f"error getting stats: {e}")
        raise


#custom validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """custom handler for validation errors"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "validation error",
            "errors": errors
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )


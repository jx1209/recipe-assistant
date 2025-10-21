#!/usr/bin/env python3
"""
Recipe Assistant API Runner
Simple script to run the FastAPI application
"""

import sys
import os
from pathlib import Path

#add src to path
sys.path.insert(0, str(Path(__file__).parent))

#ensure directories exist
Path("data").mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)

#load environment variables
from dotenv import load_dotenv
load_dotenv()

#import settings to validate configuration
from src.config.settings import get_settings

settings = get_settings()

print("=" * 60)
print(f"{settings.APP_NAME} v{settings.APP_VERSION}")
print("=" * 60)
print(f"Environment: {settings.ENVIRONMENT}")
print(f"Debug Mode: {settings.DEBUG}")
print(f"Database: {settings.DATABASE_URL}")
print(f"API Docs: http://{settings.HOST}:{settings.PORT}/docs")
print("=" * 60)
print()

#run with uvicorn
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


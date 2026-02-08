from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import endpoints
from app.config import settings
from app.utils.logger import logger

app = FastAPI(
    title="Presentation Video Agent",
    description="AI-powered presentation video generator - Multi-agent system",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(endpoints.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Presentation Video Agent starting up...")
    logger.info(f"📁 Workspace directory: {settings.WORKSPACE_DIR}")
    logger.info(f"🔧 Debug mode: {settings.DEBUG}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 Presentation Video Agent shutting down...")

@app.get("/", tags=["Health"])
def root():
    """Root endpoint - API information"""
    return {
        "name": "Presentation Video Agent",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "validate_input": "/api/v1/validate-input",
            "validate_file": "/api/v1/validate-input-file"
        }
    }

@app.get("/health", tags=["Health"])
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "workspace_exists": settings.WORKSPACE_DIR.exists()
    }


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {settings.API_HOST}:{settings.API_PORT}")
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )

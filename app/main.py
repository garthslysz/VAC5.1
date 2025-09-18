"""
Simplified gwsGPT FastAPI Application
Combines chat, rating, and document processing in a single service
Optimized for 10-20 users, easy local development and Azure deployment
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import os
import logging
from typing import List, Dict, Any, Optional

from app.chat.routes import chat_router
from app.rating.routes import rating_router  
from app.documents.routes import document_router
from app.core.auth import verify_token
from app.core.storage import storage_manager
from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Initialize global services
storage_manager = None
settings = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    global storage_manager, settings
    
    settings = get_settings()
    storage_manager = storage_manager()
    await storage_manager.initialize()
    
    logger.info("gwsGPT services initialized")
    yield
    
    # Cleanup on shutdown
    await storage_manager.cleanup()
    logger.info("gwsGPT services cleaned up")

# Create FastAPI app
app = FastAPI(
    title="gwsGPT - VAC Disability Rating Helper",
    description="Simplified API for disability rating assessments",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for local development and Azure
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://*.azurestaticapps.net",  # Azure Static Web Apps
        "https://*.azurecontainer.io"  # Azure Container Instances
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)  # Optional for development

# Health check
@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "service": "gwsGPT",
        "version": "1.0.0"
    }

# Include routers
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(rating_router, prefix="/rating", tags=["rating"])  
app.include_router(document_router, prefix="/documents", tags=["documents"])

# Simple file upload endpoint (replaces complex ingestion pipeline)
@app.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    case_id: Optional[str] = None,
    token: Optional[str] = Depends(verify_token)
):
    """
    Simple file upload and immediate processing
    Replaces the complex Durable Functions pipeline
    """
    try:
        from app.documents.processor import process_files_immediately
        
        results = await process_files_immediately(files, case_id)
        return {
            "message": f"Processed {len(files)} files",
            "case_id": case_id,
            "results": results
        }
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Simple search endpoint (replaces AI Search service)
@app.get("/search")
async def search_documents(
    query: str,
    jurisdiction: Optional[str] = None,
    chapter: Optional[str] = None,
    token: Optional[str] = Depends(verify_token)
):
    """
    Simple document search using embedded vectors
    Replaces Azure AI Search for small scale
    """
    try:
        from app.documents.search import search_embedded_documents
        
        results = await search_embedded_documents(
            query=query,
            filters={"jurisdiction": jurisdiction, "chapter": chapter}
        )
        return {"results": results}
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Development endpoints (remove in production)
if settings and settings.ENVIRONMENT == "development":
    
    @app.get("/dev/reload-rules")
    async def reload_rules():
        """Reload rating rules during development"""
        from app.rating.engines import reload_all_rules
        await reload_all_rules()
        return {"message": "Rules reloaded"}
    
    @app.get("/dev/test-vac")
    async def test_vac_rating():
        """Test VAC rating with sample data"""
        from app.rating.vac import test_sample_case
        result = await test_sample_case()
        return result

if __name__ == "__main__":
    import uvicorn
    
    # Simple local development server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Hot reload during development
        log_level="info"
    )
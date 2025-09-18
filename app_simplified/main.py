"""
VAC Canada ToD 2019 Assessment API
Focused exclusively on VAC disability rating assessments
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from typing import List, Dict, Any
import logging

from app_simplified.core.config import get_settings
from app_simplified.core.auth import verify_token
from app_simplified.chat.routes import chat_router
from app_simplified.rating.vac_canada import VACRatingEngine
from app_simplified.documents.processor import DocumentProcessor
from app_simplified.documents.search import DocumentSearch
from app_simplified.schemas.intake import CasePayload, ChatRequest
from app_simplified.schemas.results import AssessmentResult, ChatResponse

# Initialize settings
settings = get_settings()

# Initialize services
vac_rating_engine = VACRatingEngine()
document_processor = DocumentProcessor()
document_search = DocumentSearch()

app = FastAPI(
    title="VAC ToD 2019 Assessment API",
    description="Veterans Affairs Canada Table of Disabilities 2019 - Disability Rating Helper",
    version="1.0.0"
)

# CORS - use the helper property to get list from comma-separated string
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,  # Disable credentials when using specific origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Include routers
app.include_router(chat_router, prefix="/chat", tags=["chat"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "VAC ToD 2019 Assessment API",
        "version": "1.0.0",
        "environment": settings.environment
    }

@app.post("/upload", tags=["documents"])
async def upload_files(
    files: List[UploadFile] = File(...),
    case_id: str = None,
    token: Dict = Depends(verify_token)
):
    """
    Upload and process VAC assessment documents
    Supports: PDF medical reports, Word documents, previous assessments
    """
    try:
        results = []
        for file in files:
            # Process file immediately
            result = await document_processor.process_file(
                file=file,
                case_id=case_id,
                user_id=token.get("sub", "anonymous")
            )
            results.append(result)
        
        return {
            "status": "processed",
            "files": results,
            "message": f"Processed {len(files)} VAC assessment documents successfully"
        }
        
    except Exception as e:
        logging.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/assess", response_model=AssessmentResult, tags=["assessment"])
async def assess_vac_case(
    payload: CasePayload,
    token: Dict = Depends(verify_token)
):
    """
    Assess veteran disability case using VAC Canada ToD 2019
    
    This endpoint performs comprehensive disability rating assessment including:
    - Condition identification and classification
    - ToD 2019 table lookups
    - Pre-existing condition calculations
    - Quality of life impact assessment
    - Final disability rating calculation
    """
    try:
        result = await vac_rating_engine.assess_case(payload)
        return result
    except Exception as e:
        logging.error(f"VAC assessment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/calculate", tags=["rating"])
async def calculate_disability_rating(
    conditions: List[Dict[str, Any]],
    pre_existing: List[Dict[str, Any]] = None,
    token: Dict = Depends(verify_token)
):
    """
    Calculate VAC disability rating for specific conditions
    
    Args:
        conditions: List of conditions with severity ratings
        pre_existing: Optional pre-existing conditions for PCT calculations
    
    Returns:
        Final disability rating with breakdown
    """
    try:
        rating_data = {
            "conditions": conditions,
            "pre_existing": pre_existing or []
        }
        
        result = await vac_rating_engine.calculate_rating(rating_data)
        return {
            "total_disability_rating": result["total_rating"],
            "individual_conditions": result["conditions"],
            "calculation_method": result["method"],
            "pct_applied": result.get("pct_applied", False),
            "quality_of_life_impact": result.get("qol_impact")
        }
        
    except Exception as e:
        logging.error(f"Rating calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search", tags=["documents"])
async def search_vac_documents(
    query: str,
    chapter: str = None,
    condition_type: str = None,
    limit: int = 10,
    token: Dict = Depends(verify_token)
):
    """
    Search VAC ToD 2019 documents and assessment materials
    
    Args:
        query: Search terms (condition name, symptoms, etc.)
        chapter: Specific ToD chapter to search
        condition_type: Type of condition (physical, mental, etc.)
        limit: Maximum number of results
    """
    try:
        filters = {}
        if chapter:
            filters["chapter"] = chapter
        if condition_type:
            filters["condition_type"] = condition_type
            
        results = await document_search.search(
            query=query,
            filters=filters,
            limit=limit
        )
        
        return {
            "query": query,
            "filters": filters,
            "results": results,
            "count": len(results),
            "source": "VAC ToD 2019"
        }
        
    except Exception as e:
        logging.error(f"Document search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conditions", tags=["reference"])
async def get_vac_conditions(
    chapter: str = None,
    search: str = None,
    token: Dict = Depends(verify_token)
):
    """
    Get list of VAC ToD 2019 recognized conditions
    
    Args:
        chapter: Filter by ToD chapter
        search: Search condition names
    """
    try:
        conditions = await vac_rating_engine.get_conditions(
            chapter=chapter,
            search_term=search
        )
        
        return {
            "conditions": conditions,
            "count": len(conditions),
            "source": "VAC ToD 2019 Master Tables"
        }
        
    except Exception as e:
        logging.error(f"Conditions lookup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chapters", tags=["reference"])
async def get_vac_chapters(token: Dict = Depends(verify_token)):
    """Get all VAC ToD 2019 chapters and their descriptions"""
    try:
        chapters = await vac_rating_engine.get_chapters()
        
        return {
            "chapters": chapters,
            "count": len(chapters),
            "source": "VAC ToD 2019",
            "description": "Table of Disabilities chapters covering different body systems and condition types"
        }
        
    except Exception as e:
        logging.error(f"Chapters lookup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cases/{case_id}/files", tags=["cases"])
async def get_case_files(
    case_id: str,
    token: Dict = Depends(verify_token)
):
    """Get all files associated with a VAC assessment case"""
    try:
        files = await document_processor.get_case_files(case_id)
        return {
            "case_id": case_id,
            "files": files,
            "count": len(files)
        }
    except Exception as e:
        logging.error(f"Case files lookup error: {e}")
        raise HTTPException(status_code=404, detail="Case not found")

@app.get("/cases/{case_id}/history", tags=["cases"])
async def get_case_assessment_history(
    case_id: str,
    token: Dict = Depends(verify_token)
):
    """Get assessment history for a specific case"""
    try:
        history = await vac_rating_engine.get_case_history(case_id)
        return {
            "case_id": case_id,
            "assessments": history,
            "count": len(history)
        }
    except Exception as e:
        logging.error(f"Case history lookup error: {e}")
        raise HTTPException(status_code=404, detail="Case history not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=settings.port,
        log_level=settings.log_level.lower()
    )
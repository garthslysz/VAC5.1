"""
Pydantic schemas for VAC assessment requests
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# Input schemas
class VACCondition(BaseModel):
    """Individual condition for VAC assessment"""
    name: str = Field(..., description="Condition name (e.g., 'PTSD', 'Lower back pain')")
    symptoms: List[str] = Field(default=[], description="List of symptoms")
    severity: str = Field(..., description="Severity level (mild, moderate, severe, very_severe, extreme)")
    onset_date: Optional[str] = Field(None, description="When condition began")
    service_connection: Optional[str] = Field(None, description="How condition relates to military service")

class VACCasePayload(BaseModel):
    """Complete VAC assessment case payload"""
    case_id: Optional[str] = Field(None, description="Unique case identifier")
    veteran_info: Optional[Dict[str, Any]] = Field(None, description="Basic veteran information")
    conditions: List[VACCondition] = Field(..., description="List of conditions to assess")
    pre_existing: Optional[List[VACCondition]] = Field(default=[], description="Pre-existing conditions for PCT calculations")
    medical_evidence: Optional[List[Dict[str, Any]]] = Field(default=[], description="Medical evidence documents")
    quality_of_life_statement: Optional[str] = Field(None, description="Veteran's quality of life impact statement")
    prior_assessments: Optional[List[Dict]] = Field(default=[], description="Previous VAC assessments")
    assessment_date: Optional[str] = Field(None, description="Date of assessment")

class ChatRequest(BaseModel):
    """Chat request for VAC assessment conversation"""
    message: str = Field(..., description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation identifier") 
    case_id: Optional[str] = Field(None, description="Associated VAC case ID")
    files: Optional[List[str]] = Field(None, description="Attached medical document URLs")
    context: Optional[str] = Field(None, description="Additional context (adjudicator notes, etc.)")

class DocumentUpload(BaseModel):
    """VAC document upload metadata"""
    filename: str = Field(..., description="Name of uploaded file")
    file_type: str = Field(..., description="File type (PDF, DOCX, etc.)")
    case_id: Optional[str] = Field(None, description="Associated VAC case")
    document_type: Optional[str] = Field(None, description="Type of document (medical_report, prior_assessment, etc.)")
    description: Optional[str] = Field(None, description="Document description")

class ConditionSearch(BaseModel):
    """Search parameters for VAC conditions"""
    query: str = Field(..., description="Search term")
    chapter: Optional[str] = Field(None, description="Specific ToD chapter")
    condition_type: Optional[str] = Field(None, description="Type of condition")

# Legacy compatibility - keeping CasePayload as alias
CasePayload = VACCasePayload

"""
VAC assessment response schemas
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# Output schemas
class VACConditionAssessment(BaseModel):
    """Individual condition assessment result"""
    condition: str = Field(..., description="Condition name")
    tod_condition_id: Optional[str] = Field(None, description="VAC ToD condition identifier")
    chapter: Optional[str] = Field(None, description="ToD chapter")
    tod_found: bool = Field(..., description="Whether condition was found in ToD 2019")
    rating: int = Field(..., description="Individual disability rating percentage")
    rating_rationale: Optional[str] = Field(None, description="Explanation of rating determination")
    symptoms_matched: Optional[List[str]] = Field(None, description="Symptoms that matched ToD criteria")
    assessment_criteria_met: Optional[List[str]] = Field(None, description="Assessment criteria satisfied")
    medical_evidence_support: Optional[Dict[str, Any]] = Field(None, description="Medical evidence evaluation")

class VACQualityOfLifeAssessment(BaseModel):
    """Quality of life impact assessment"""
    impact_level: str = Field(..., description="Overall impact level")
    total_rating: int = Field(..., description="Combined disability rating")
    functional_limitations: List[str] = Field(..., description="Identified functional limitations")
    recommendations: List[str] = Field(..., description="Quality of life recommendations")

class VACCombinedRating(BaseModel):
    """Combined disability rating calculation"""
    total_rating: int = Field(..., description="Final combined disability percentage")
    individual_ratings: List[int] = Field(..., description="Individual condition ratings")
    method: str = Field(..., description="Calculation method used")
    pct_applied: bool = Field(..., description="Whether pre-existing condition table was applied")
    confidence: str = Field(..., description="Assessment confidence level")

class VACAssessmentResult(BaseModel):
    """Complete VAC assessment result"""
    case_id: Optional[str] = Field(None, description="Case identifier")
    assessment_date: Optional[str] = Field(None, description="Date of assessment")
    total_disability_rating: int = Field(..., description="Final disability rating percentage")
    individual_conditions: List[VACConditionAssessment] = Field(..., description="Individual condition assessments")
    combined_rating_breakdown: VACCombinedRating = Field(..., description="Combined rating calculation details")
    quality_of_life_impact: VACQualityOfLifeAssessment = Field(..., description="Quality of life assessment")
    recommendations: List[str] = Field(..., description="Overall recommendations")
    tod_version: str = Field(default="VAC 2019", description="Table of Disabilities version")
    assessment_confidence: str = Field(..., description="Overall confidence in assessment")
    assessed_at: datetime = Field(default_factory=datetime.now, description="Timestamp of assessment")
    assessor: str = Field(default="VAC Assessment System", description="System or person who performed assessment")

class VACConditionInfo(BaseModel):
    """VAC condition information"""
    id: str = Field(..., description="Condition identifier")
    name: str = Field(..., description="Condition name")
    chapter: str = Field(..., description="ToD chapter")
    symptoms: List[str] = Field(..., description="Associated symptoms")

class VACChapterInfo(BaseModel):
    """VAC ToD chapter information"""
    id: str = Field(..., description="Chapter identifier")
    title: str = Field(..., description="Chapter title")
    description: str = Field(..., description="Chapter description")
    condition_count: int = Field(..., description="Number of conditions in chapter")

class ChatResponse(BaseModel):
    """Chat response payload"""
    message: str = Field(..., description="Assistant response")
    conversation_id: str = Field(..., description="Conversation identifier")
    function_calls: Optional[List[Dict]] = Field(None, description="Functions called during response")
    attachments: Optional[List[Dict]] = Field(None, description="Response attachments")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    case_context: Optional[Dict[str, Any]] = Field(None, description="VAC case context if applicable")

class VACDocumentSearchResult(BaseModel):
    """VAC document search result"""
    content: str = Field(..., description="Matching content from ToD or medical documents")
    source: str = Field(..., description="Source document (ToD chapter, medical report, etc.)")
    chapter: Optional[str] = Field(None, description="ToD chapter if applicable")
    document_type: str = Field(..., description="Type of document")
    relevance_score: float = Field(..., description="Relevance score 0-1")
    
class FileProcessingResult(BaseModel):
    """File processing result for VAC documents"""
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File type (PDF, DOCX, etc.)")
    status: str = Field(..., description="Processing status (processed, failed, pending)")
    extracted_text: Optional[str] = Field(None, description="Extracted text content")
    document_classification: Optional[str] = Field(None, description="Classified document type")
    medical_conditions_detected: Optional[List[str]] = Field(None, description="Detected medical conditions")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    error_message: Optional[str] = Field(None, description="Error message if processing failed")
    processed_at: datetime = Field(default_factory=datetime.now, description="Processing timestamp")

# Legacy compatibility - keeping AssessmentResult as alias
AssessmentResult = VACAssessmentResult

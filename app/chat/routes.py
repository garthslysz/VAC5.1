"""
Chat routes - handles conversation with the VAC rating assistant
Replicates your OpenAI GPT behavior using Azure OpenAI API
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from app.core.auth import verify_token
from app.core.conversation import ConversationManager
from app.core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    files: Optional[List[str]] = None  # File URLs if uploaded
    case_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    case_id: Optional[str] = None
    assessment_result: Optional[Dict[str, Any]] = None
    function_calls: Optional[List[Dict[str, Any]]] = None

@router.post("/", response_model=ChatResponse)
async def chat_with_assistant(
    request: ChatMessage,
    token: Optional[str] = Depends(verify_token)
):
    """
    Main chat endpoint - replicates your OpenAI GPT behavior
    Handles:
    - Initial assessment requests ("Please assess an entitlement")
    - Follow-up questions and clarifications
    - Document analysis and rating calculations
    """
    try:
        # Get user ID from token (or use anonymous for development)
        user_id = token.get("sub") if token else "dev-user"
        
        # Initialize conversation manager
        conversation = ConversationManager(user_id=user_id)
        
        # Process the chat message
        response = await conversation.process_message(request)
        
        return response
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{case_id}")
async def get_chat_history(
    case_id: str,
    token: Optional[str] = Depends(verify_token)
):
    """Get chat history for a specific case"""
    try:
        user_id = token.get("sub") if token else "dev-user"
        conversation = ConversationManager(user_id=user_id)
        
        history = await conversation.get_case_history(case_id)
        return {"history": history}
        
    except Exception as e:
        logger.error(f"History retrieval error: {e}")
        raise HTTPException(status_code=404, detail="Case history not found")

@router.delete("/history/{case_id}")
async def clear_chat_history(
    case_id: str,
    token: Optional[str] = Depends(verify_token)
):
    """Clear chat history for a case"""
    try:
        user_id = token.get("sub") if token else "dev-user"
        conversation = ConversationManager(user_id=user_id)
        
        await conversation.clear_case_history(case_id)
        return {"message": "Chat history cleared"}
        
    except Exception as e:
        logger.error(f"History clear error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
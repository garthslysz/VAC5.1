"""
Chat routes for VAC assessment conversations
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
import logging
import uuid
from datetime import datetime

from app_simplified.core.auth import verify_token
from app_simplified.core.openai_client import vac_client
from app_simplified.core.vac_data import vac_data_manager
from app_simplified.schemas.intake import ChatRequest
from app_simplified.schemas.results import ChatResponse

logger = logging.getLogger(__name__)

chat_router = APIRouter()

# In-memory conversation storage (for demo - would use database in production)
conversations = {}

@chat_router.post("/", response_model=ChatResponse)
async def chat_with_vac_assistant(
    request: ChatRequest,
    token: Dict = Depends(verify_token)
):
    """
    Main chat endpoint for VAC assessment conversations
    """
    try:
        # Get or create conversation ID
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Get conversation history
        conversation = conversations.get(conversation_id, {
            "id": conversation_id,
            "created_at": datetime.now().isoformat(),
            "messages": [],
            "case_id": request.case_id,
            "user_id": token.get("sub", "anonymous")
        })
        
        # Add user message to conversation
        user_message = {
            "role": "user",
            "content": request.message,
            "timestamp": datetime.now().isoformat()
        }
        
        if request.context:
            user_message["context"] = request.context
        
        conversation["messages"].append(user_message)
        
        # Prepare messages for OpenAI
        openai_messages = []
        for msg in conversation["messages"]:
            openai_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Define available functions
        functions = _get_chat_functions()
        
        # Get AI response
        ai_response = await vac_client.chat_completion(
            messages=openai_messages,
            functions=functions,
            temperature=0.3,
            max_tokens=2000
        )
        
        # Process function calls if present
        function_results = []
        if ai_response.get("function_calls"):
            function_results = await _process_function_calls(
                ai_response["function_calls"],
                request.case_id
            )
        
        # Add AI response to conversation
        assistant_message = {
            "role": "assistant", 
            "content": ai_response.get("content", ""),
            "timestamp": datetime.now().isoformat()
        }
        
        if function_results:
            assistant_message["function_results"] = function_results
        
        conversation["messages"].append(assistant_message)
        conversation["updated_at"] = datetime.now().isoformat()
        
        # Store updated conversation
        conversations[conversation_id] = conversation
        
        # Prepare response
        response = ChatResponse(
            message=ai_response.get("content", ""),
            conversation_id=conversation_id,
            function_calls=function_results if function_results else None,
            metadata={
                "message_count": len(conversation["messages"]),
                "case_id": request.case_id,
                "finish_reason": ai_response.get("finish_reason")
            }
        )
        
        if request.case_id:
            response.case_context = {
                "case_id": request.case_id,
                "message_count": len(conversation["messages"])
            }
        
        return response
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")

@chat_router.get("/{conversation_id}/history")
async def get_conversation_history(
    conversation_id: str,
    token: Dict = Depends(verify_token)
):
    """Get conversation history"""
    try:
        conversation = conversations.get(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Filter out internal metadata for response
        return {
            "conversation_id": conversation_id,
            "messages": conversation["messages"],
            "case_id": conversation.get("case_id"),
            "created_at": conversation.get("created_at"),
            "updated_at": conversation.get("updated_at"),
            "message_count": len(conversation["messages"])
        }
        
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    token: Dict = Depends(verify_token)
):
    """Delete a conversation"""
    try:
        if conversation_id not in conversations:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        del conversations[conversation_id]
        
        return {"message": f"Conversation {conversation_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.get("/")
async def list_conversations(
    token: Dict = Depends(verify_token),
    limit: int = 50
):
    """List user's conversations"""
    try:
        user_id = token.get("sub", "anonymous")
        user_conversations = []
        
        for conv_id, conversation in conversations.items():
            if conversation.get("user_id") == user_id:
                user_conversations.append({
                    "conversation_id": conv_id,
                    "case_id": conversation.get("case_id"),
                    "created_at": conversation.get("created_at"),
                    "updated_at": conversation.get("updated_at"),
                    "message_count": len(conversation.get("messages", []))
                })
        
        # Sort by updated_at descending
        user_conversations.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        
        return {
            "conversations": user_conversations[:limit],
            "total": len(user_conversations)
        }
        
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _get_chat_functions() -> List[Dict]:
    """Get available functions for chat context"""
    return [
        {
            "name": "search_vac_documents",
            "description": "Search VAC Table of Disabilities and supporting documents",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for VAC documents"
                    },
                    "chapter": {
                        "type": "string", 
                        "description": "Specific VAC ToD chapter to search"
                    },
                    "condition_type": {
                        "type": "string",
                        "description": "Type of condition (mental, physical, etc.)"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "assess_vac_condition", 
            "description": "Assess individual condition using VAC ToD 2019 criteria",
            "parameters": {
                "type": "object",
                "properties": {
                    "condition_name": {
                        "type": "string",
                        "description": "Name of the medical condition"
                    },
                    "symptoms": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of symptoms present"
                    },
                    "severity": {
                        "type": "string",
                        "description": "Severity level (mild, moderate, severe, etc.)"
                    },
                    "medical_evidence": {
                        "type": "string",
                        "description": "Relevant medical evidence for this condition"
                    }
                },
                "required": ["condition_name", "symptoms", "severity"]
            }
        },
        {
            "name": "get_vac_condition_info",
            "description": "Get detailed VAC ToD information for a specific condition",
            "parameters": {
                "type": "object",
                "properties": {
                    "condition_name": {
                        "type": "string",
                        "description": "Name of condition to look up"
                    }
                },
                "required": ["condition_name"]
            }
        },
        {
            "name": "list_vac_chapters",
            "description": "List all VAC Table of Disabilities chapters",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    ]

async def _process_function_calls(
    function_calls: List[Dict],
    case_id: Optional[str] = None
) -> List[Dict]:
    """Process function calls from AI and return results"""
    results = []
    
    for call in function_calls:
        function_name = call.get("name")
        arguments = call.get("arguments", {})
        call_id = call.get("id")
        
        try:
            if function_name == "search_vac_documents":
                result = await _search_vac_documents(
                    query=arguments.get("query", ""),
                    chapter=arguments.get("chapter"),
                    condition_type=arguments.get("condition_type")
                )
            
            elif function_name == "assess_vac_condition":
                result = await _assess_vac_condition(
                    condition_name=arguments.get("condition_name", ""),
                    symptoms=arguments.get("symptoms", []),
                    severity=arguments.get("severity", ""),
                    medical_evidence=arguments.get("medical_evidence", "")
                )
            
            elif function_name == "get_vac_condition_info":
                result = await _get_vac_condition_info(
                    condition_name=arguments.get("condition_name", "")
                )
            
            elif function_name == "list_vac_chapters":
                result = await _list_vac_chapters()
            
            else:
                result = {"error": f"Unknown function: {function_name}"}
            
            results.append({
                "function": function_name,
                "call_id": call_id,
                "arguments": arguments,
                "result": result,
                "status": "success" if "error" not in result else "error"
            })
            
        except Exception as e:
            logger.error(f"Function call error for {function_name}: {e}")
            results.append({
                "function": function_name,
                "call_id": call_id,
                "arguments": arguments,
                "result": {"error": str(e)},
                "status": "error"
            })
    
    return results

async def _search_vac_documents(
    query: str,
    chapter: Optional[str] = None,
    condition_type: Optional[str] = None
) -> Dict[str, Any]:
    """Search VAC documents"""
    try:
        results = vac_data_manager.search_conditions(
            query=query,
            chapter=chapter,
            limit=10
        )
        
        return {
            "query": query,
            "results": results,
            "count": len(results),
            "source": "VAC Table of Disabilities 2019"
        }
        
    except Exception as e:
        logger.error(f"VAC document search error: {e}")
        return {"error": f"Search failed: {str(e)}"}

async def _assess_vac_condition(
    condition_name: str,
    symptoms: List[str],
    severity: str,
    medical_evidence: str
) -> Dict[str, Any]:
    """Assess a VAC condition"""
    try:
        # Use VAC data manager to calculate rating
        result = vac_data_manager.calculate_basic_rating(
            condition_name=condition_name,
            severity=severity,
            symptoms=symptoms
        )
        
        # Add medical evidence analysis
        result["medical_evidence_summary"] = medical_evidence[:500] + "..." if len(medical_evidence) > 500 else medical_evidence
        result["evidence_adequacy"] = "adequate" if len(medical_evidence) > 100 else "limited"
        
        return result
        
    except Exception as e:
        logger.error(f"VAC condition assessment error: {e}")
        return {"error": f"Assessment failed: {str(e)}"}

async def _get_vac_condition_info(condition_name: str) -> Dict[str, Any]:
    """Get VAC condition information"""
    try:
        condition = vac_data_manager.find_condition(condition_name)
        
        if not condition:
            return {
                "condition_name": condition_name,
                "found": False,
                "message": f"Condition '{condition_name}' not found in VAC ToD 2019"
            }
        
        return {
            "condition_name": condition_name,
            "found": True,
            "condition_info": condition,
            "chapter": condition.get("chapter", ""),
            "symptoms": condition.get("symptoms", []),
            "rating_criteria": condition.get("rating_criteria", {}),
            "source": "VAC Table of Disabilities 2019"
        }
        
    except Exception as e:
        logger.error(f"VAC condition lookup error: {e}")
        return {"error": f"Lookup failed: {str(e)}"}

async def _list_vac_chapters() -> Dict[str, Any]:
    """List VAC ToD chapters"""
    try:
        chapters = vac_data_manager.get_all_chapters()
        
        return {
            "chapters": chapters,
            "count": len(chapters),
            "source": "VAC Table of Disabilities 2019"
        }
        
    except Exception as e:
        logger.error(f"VAC chapters listing error: {e}")
        return {"error": f"Chapters listing failed: {str(e)}"}

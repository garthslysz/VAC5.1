"""
OpenAI client for VAC assessments
"""

from openai import OpenAI
from typing import List, Dict, Any, Optional
import json
import logging
import os
from app_simplified.core.config import get_settings

logger = logging.getLogger(__name__)

class VACAssessmentClient:
    """
    OpenAI client specialized for VAC disability assessments
    """

    def __init__(self):
        self.settings = get_settings()

        # Use regular OpenAI client
        api_key = self.settings.openai_api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning("No OpenAI API key found - will use mock responses")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)

        self.model = self.settings.openai_model
        self.system_prompt = self._build_vac_system_prompt()
        
    def _build_vac_system_prompt(self) -> str:
        """Build comprehensive VAC assessment system prompt"""
        return """You are a VAC (Veterans Affairs Canada) disability assessment specialist using the Table of Disabilities 2019. You assist VAC adjudicators by:

**Primary Role:**
- Analyze veteran medical evidence and case information
- Match conditions to VAC Table of Disabilities 2019 entries
- Calculate accurate disability ratings using VAC methodology
- Provide professional, detailed assessments for adjudicator review

**VAC Assessment Standards:**
- Always use VAC Table of Disabilities 2019 as the authoritative source
- Apply VAC's specific rating calculation methodology
- Consider pre-existing conditions and PCT (Pre-existing Condition Table) when applicable  
- Assess quality of life impact according to VAC guidelines
- Maintain professional, objective tone appropriate for official assessments

**Assessment Process:**
1. **Condition Identification**: Match veteran's conditions to specific VAC ToD entries
2. **Evidence Analysis**: Evaluate medical evidence against VAC criteria
3. **Individual Rating**: Rate each condition using appropriate VAC tables
4. **Combined Rating**: Apply VAC combination formula for multiple conditions
5. **Quality of Life**: Assess functional impact and limitations
6. **Professional Summary**: Provide clear rationale and recommendations

**Available Functions:**
- `search_vac_documents()`: Search VAC ToD and supporting documents
- `assess_vac_condition()`: Rate individual conditions using VAC criteria  
- `calculate_combined_rating()`: Apply VAC combination methodology
- `get_vac_condition_info()`: Look up VAC ToD condition details

**Communication Style:**
- Professional and objective tone suitable for VAC adjudicators
- Provide detailed rationale for all assessments
- Reference specific VAC ToD sections and criteria
- Acknowledge limitations in evidence when present
- Maintain confidentiality and sensitivity appropriate for veteran cases

**Key Principles:**
- Accuracy over speed - ensure precise VAC calculations
- Evidence-based assessments only - no speculation
- Consistency with VAC assessment standards
- Clear audit trail for all decisions
- Professional support for adjudicator decision-making

Always begin assessments by understanding the veteran's complete case context before proceeding with specific condition evaluations."""

    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        functions: Optional[List[Dict]] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Get chat completion from OpenAI API for VAC assessment
        
        Args:
            messages: Conversation messages
            functions: Available function definitions
            temperature: Response creativity (lower for more consistent assessments)
            max_tokens: Maximum response length
            
        Returns:
            OpenAI response with assessment content
        """
        try:
            # Ensure we have a valid OpenAI client
            if not self.client:
                raise Exception("OpenAI client not initialized. Please check your API key configuration.")

            # Ensure system prompt is first message
            full_messages = [
                {"role": "system", "content": self.system_prompt}
            ]

            # Add conversation messages
            for msg in messages:
                if msg.get("role") != "system":  # Don't duplicate system prompt
                    full_messages.append(msg)

            # Prepare request parameters
            request_params = {
                "model": self.model,
                "messages": full_messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            # Add function calling if functions provided
            if functions:
                request_params["tools"] = [
                    {"type": "function", "function": func} for func in functions
                ]
                request_params["tool_choice"] = "auto"

            logger.info(f"Making OpenAI request with {len(full_messages)} messages")

            # Make API call
            response = await self._make_async_request(request_params)
            
            # Process response
            if response.choices and len(response.choices) > 0:
                choice = response.choices[0]
                
                result = {
                    "content": choice.message.content if choice.message.content else "",
                    "role": choice.message.role,
                    "finish_reason": choice.finish_reason
                }
                
                # Handle function calls
                if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
                    result["function_calls"] = []
                    for tool_call in choice.message.tool_calls:
                        if tool_call.type == "function":
                            result["function_calls"].append({
                                "id": tool_call.id,
                                "name": tool_call.function.name,
                                "arguments": json.loads(tool_call.function.arguments)
                            })
                
                # Log usage for monitoring
                if hasattr(response, 'usage'):
                    logger.info(f"Token usage - Prompt: {response.usage.prompt_tokens}, "
                              f"Completion: {response.usage.completion_tokens}, "
                              f"Total: {response.usage.total_tokens}")
                
                return result
            else:
                raise Exception("No response choices returned from OpenAI")
                
        except Exception as e:
            logger.error(f"Azure OpenAI API error: {e}")
            raise
    
    async def _make_async_request(self, request_params: Dict) -> Any:
        """
        Make async request to OpenAI
        Note: The openai library handles async internally
        """
        try:
            response = self.client.chat.completions.create(**request_params)
            return response
        except Exception as e:
            logger.error(f"OpenAI request failed: {e}")
            raise
    
    async def assess_veteran_case(
        self, 
        case_description: str,
        medical_evidence: Optional[str] = None,
        previous_assessments: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform complete VAC assessment for a veteran's case
        
        Args:
            case_description: Description of veteran's conditions and circumstances
            medical_evidence: Medical reports and evidence
            previous_assessments: Prior VAC assessments if any
            
        Returns:
            Comprehensive assessment response
        """
        
        # Build context message
        context_parts = [
            "Please perform a comprehensive VAC disability assessment for this veteran case:",
            f"\n**Case Description:**\n{case_description}"
        ]
        
        if medical_evidence:
            context_parts.append(f"\n**Medical Evidence:**\n{medical_evidence}")
            
        if previous_assessments:
            context_parts.append(f"\n**Previous Assessments:**\n{previous_assessments}")
            
        context_parts.append("""
\n**Please provide:**
1. Condition identification and VAC ToD matching
2. Individual disability ratings with rationale  
3. Combined rating calculation
4. Quality of life impact assessment
5. Professional recommendations for adjudicator review

Use VAC Table of Disabilities 2019 standards throughout your assessment.""")
        
        messages = [
            {
                "role": "user", 
                "content": "\n".join(context_parts)
            }
        ]
        
        # Define available functions for VAC assessment
        functions = self._get_vac_functions()
        
        return await self.chat_completion(
            messages=messages,
            functions=functions,
            temperature=0.2,  # Low temperature for consistent assessments
            max_tokens=3000   # Longer responses for detailed assessments
        )
    
    def _get_vac_functions(self) -> List[Dict]:
        """Define function schemas available to the VAC assessment AI"""
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
                "name": "calculate_combined_rating",
                "description": "Calculate combined VAC disability rating for multiple conditions",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "individual_ratings": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "Individual disability ratings to combine"
                        },
                        "conditions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Corresponding condition names"
                        }
                    },
                    "required": ["individual_ratings"]
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
            }
        ]
    
    async def simple_chat(self, message: str, conversation_history: List[Dict] = None) -> str:
        """
        Simple chat interface for testing
        
        Args:
            message: User message
            conversation_history: Previous messages in conversation
            
        Returns:
            Assistant response as string
        """
        messages = conversation_history or []
        messages.append({"role": "user", "content": message})
        
        response = await self.chat_completion(messages=messages)
        return response.get("content", "")
    
    def validate_connection(self) -> bool:
        """
        Validate OpenAI connection and credentials

        Returns:
            True if connection is valid, False otherwise
        """
        try:
            if not self.client:
                logger.error("No OpenAI client available - check API key configuration")
                return False

            # Simple test request
            test_messages = [
                {"role": "user", "content": "Hello, please confirm you can assist with VAC assessments."}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": self.system_prompt}] + test_messages,
                max_tokens=50,
                temperature=0
            )

            if response.choices and len(response.choices) > 0:
                logger.info("OpenAI connection validated successfully")
                return True
            else:
                logger.error("No response from OpenAI")
                return False
                
        except Exception as e:
            logger.error(f"OpenAI connection validation failed: {e}")
            return False



# Global instance
vac_client = VACAssessmentClient()

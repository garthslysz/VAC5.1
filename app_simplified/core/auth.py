"""
Authentication utilities for VAC assessment system
"""

from typing import Dict, Optional
import logging
from fastapi import HTTPException, status
from app_simplified.core.config import get_settings

logger = logging.getLogger(__name__)

async def verify_token(token: Optional[str] = None) -> Dict[str, any]:
    """
    Verify authentication token
    For demo purposes, this is simplified
    In production, would integrate with Azure AD or other auth systems
    """
    settings = get_settings()
    
    # If auth is disabled for development, return mock user
    if settings.auth_disabled:
        return {
            "sub": "demo_adjudicator",
            "name": "Demo Adjudicator",
            "email": "demo@vac.gc.ca",
            "roles": ["vac_adjudicator"],
            "authenticated": True
        }
    
    # In production, would validate JWT token here
    # For now, return basic auth info
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Mock validation - replace with real auth
    return {
        "sub": "authenticated_user", 
        "name": "VAC Adjudicator",
        "email": "adjudicator@vac.gc.ca",
        "roles": ["vac_adjudicator"],
        "authenticated": True
    }

def require_role(required_role: str):
    """
    Decorator to require specific role for endpoint access
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Would implement role checking here
            return await func(*args, **kwargs)
        return wrapper
    return decorator

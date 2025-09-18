#!/usr/bin/env python3
"""
Quick API key validation script
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app_simplified.core.config import get_settings

def check_api_key():
    """Check if OpenAI API key is properly configured"""
    print("🔑 Checking OpenAI API Key Configuration...")
    
    settings = get_settings()
    
    if not settings.openai_api_key:
        print("❌ No OpenAI API key found in environment")
        return False
    
    if settings.openai_api_key == "your-openai-api-key-here":
        print("❌ OpenAI API key is still using placeholder value")
        print("💡 Edit the .env file and replace 'your-openai-api-key-here' with your actual API key")
        return False
    
    if not settings.openai_api_key.startswith(('sk-', 'sk-proj-')):
        print("⚠️  OpenAI API key format looks unusual (should start with 'sk-' or 'sk-proj-')")
        print("   Please double-check your key")
    
    key_preview = settings.openai_api_key[:10] + "..." + settings.openai_api_key[-4:]
    print(f"✅ OpenAI API key configured: {key_preview}")
    print(f"ℹ️  Using model: {settings.openai_model}")
    return True

if __name__ == "__main__":
    success = check_api_key()
    if success:
        print("\n🚀 Ready to test! Run: python test_setup.py")
    else:
        print("\n🔧 Please fix the API key configuration above")
    sys.exit(0 if success else 1)

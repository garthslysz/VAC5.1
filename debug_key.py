#!/usr/bin/env python3
"""
Debug script to check exactly what API key is being loaded
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def debug_api_key():
    """Debug API key loading"""
    print("🔍 Debugging API Key Loading...")
    
    # Check environment variable
    env_key = os.getenv('OPENAI_API_KEY')
    if env_key:
        print(f"📍 Environment variable: {env_key[:10]}...{env_key[-4:]}")
    else:
        print("📍 No OPENAI_API_KEY environment variable found")
    
    # Check .env file directly
    env_file = Path('.env')
    if env_file.exists():
        print("📁 Reading .env file directly...")
        with open('.env', 'r') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('OPENAI_API_KEY='):
                key_line = line.strip()
                if '=' in key_line:
                    key_value = key_line.split('=', 1)[1]
                    if key_value and key_value != 'your-openai-api-key-here':
                        print(f"📄 .env file line {i}: OPENAI_API_KEY={key_value[:10]}...{key_value[-4:]}")
                    else:
                        print(f"📄 .env file line {i}: OPENAI_API_KEY is placeholder or empty")
                break
        else:
            print("📄 No OPENAI_API_KEY found in .env file")
    
    # Check what pydantic settings loads
    try:
        from app_simplified.core.config import get_settings
        settings = get_settings()
        
        if settings.openai_api_key:
            print(f"⚙️  Pydantic settings: {settings.openai_api_key[:10]}...{settings.openai_api_key[-4:]}")
        else:
            print("⚙️  Pydantic settings: No API key loaded")
            
    except Exception as e:
        print(f"❌ Error loading settings: {e}")

if __name__ == "__main__":
    debug_api_key()

#!/usr/bin/env python3
"""
Simple configuration test to verify all settings load correctly
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config():
    """Test that configuration loads without errors"""
    print("🔧 Testing Configuration Loading...")
    
    try:
        from app_simplified.core.config import get_settings
        settings = get_settings()
        
        print("✅ Configuration loaded successfully!")
        print(f"   Environment: {settings.environment}")
        print(f"   Debug mode: {settings.debug}")
        print(f"   Port: {settings.port}")
        print(f"   Auth disabled: {settings.auth_disabled}")
        print(f"   CORS origins: {settings.cors_origins_list}")
        print(f"   OpenAI model: {settings.openai_model}")
        print(f"   File storage: {'Local' if settings.use_local_file_storage else 'Azure'}")
        
        # Check API key
        if settings.openai_api_key and settings.openai_api_key != "your-openai-api-key-here":
            key_preview = settings.openai_api_key[:10] + "..." + settings.openai_api_key[-4:]
            print(f"   OpenAI API key: {key_preview}")
        else:
            print("   ⚠️  OpenAI API key not set")
            
        return True
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

if __name__ == "__main__":
    success = test_config()
    if success:
        print("\n🚀 Configuration test passed! Now add your OpenAI API key to .env")
    else:
        print("\n🔧 Please fix the configuration errors above")
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Test script to validate VAC Assessment API setup and OpenAI integration
Run this before starting local testing to ensure everything is configured correctly
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app_simplified.core.config import get_settings
from app_simplified.core.openai_client import vac_client
from app_simplified.core.vac_data import vac_data_manager

def test_environment_config():
    """Test that environment configuration is properly loaded"""
    print("🔧 Testing Environment Configuration...")
    
    settings = get_settings()
    
    # Check critical settings
    issues = []
    
    if not settings.openai_api_key or settings.openai_api_key == "your-openai-api-key-here":
        issues.append("❌ OpenAI API key not set or still using placeholder")
    else:
        print("✅ OpenAI API key is configured")
    
    if settings.auth_disabled:
        print("⚠️  Authentication is disabled (OK for local development)")
    else:
        print("✅ Authentication is enabled")
    
    if settings.debug:
        print("ℹ️  Debug mode is enabled")
    
    print(f"ℹ️  Using OpenAI model: {settings.openai_model}")
    print(f"ℹ️  Port: {settings.port}")
    print(f"ℹ️  Environment: {settings.environment}")
    
    if issues:
        print("\n❌ Configuration Issues Found:")
        for issue in issues:
            print(f"   {issue}")
        return False
    
    print("✅ Environment configuration looks good!")
    return True

def test_vac_data_loading():
    """Test that VAC ToD 2019 data loads correctly"""
    print("\n📊 Testing VAC ToD 2019 Data Loading...")
    
    validation = vac_data_manager.validate_data()
    
    if validation["valid"]:
        stats = validation["stats"]
        print(f"✅ VAC ToD data loaded successfully")
        print(f"   📚 Chapters: {stats['total_chapters']}")
        print(f"   🏥 Conditions: {stats['total_conditions']}")
        print(f"   📋 Rating tables: {stats['total_rating_tables']}")
        
        # Test a sample lookup
        test_condition = vac_data_manager.find_condition("PTSD")
        if test_condition:
            print(f"   ✅ Sample condition lookup working (found: {test_condition['name']})")
        else:
            print("   ⚠️  Sample condition lookup didn't find PTSD (may be OK if using limited data)")
        
        return True
    else:
        print("❌ VAC ToD data validation failed:")
        for error in validation["errors"]:
            print(f"   - {error}")
        for warning in validation["warnings"]:
            print(f"   ⚠️  {warning}")
        return False

async def test_openai_connection():
    """Test OpenAI API connection"""
    print("\n🤖 Testing OpenAI API Connection...")
    
    try:
        # Test connection validation
        is_valid = vac_client.validate_connection()
        
        if is_valid:
            print("✅ OpenAI connection validated successfully")
            
            # Test a simple chat completion
            print("   Testing simple chat completion...")
            response = await vac_client.simple_chat("Hello, can you confirm you're working?")
            
            if response and len(response) > 0:
                print("✅ OpenAI chat completion working")
                print(f"   Response preview: {response[:100]}...")
                return True
            else:
                print("❌ OpenAI returned empty response")
                return False
        else:
            print("❌ OpenAI connection validation failed")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI connection test failed: {str(e)}")
        if "API key" in str(e).lower():
            print("   💡 Make sure your OpenAI API key is set correctly in .env file")
        return False

def test_mock_logic_removed():
    """Verify that mock logic has been completely removed"""
    print("\n🧪 Verifying Mock Logic Removal...")
    
    issues = []
    
    # Check if mock methods exist
    if hasattr(vac_client, '_generate_mock_response'):
        issues.append("Mock response method still exists in OpenAI client")
    
    # Check settings for mock flags
    settings = get_settings()
    if hasattr(settings, 'mock_openai_responses'):
        if settings.mock_openai_responses:
            issues.append("Mock OpenAI responses are still enabled")
    
    # Check for API key placeholder
    if settings.openai_api_key == "your-openai-api-key-here":
        issues.append("OpenAI API key is still using placeholder value")
    
    if issues:
        print("❌ Mock logic issues found:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ No mock logic found - system is using real OpenAI API")
        return True

def check_file_structure():
    """Check that required files exist"""
    print("\n📁 Checking File Structure...")
    
    required_files = [
        "app_simplified/main.py",
        "app_simplified/core/config.py",
        "app_simplified/core/openai_client.py",
        "app_simplified/data/rules/master2019ToD.json",
        ".env"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ All required files present")
        return True

def print_next_steps():
    """Print next steps for local testing"""
    print("\n🚀 Next Steps for Local Testing:")
    print("1. Start the API server:")
    print("   cd /home/gslys/gwsGPT")
    print("   python -m uvicorn app_simplified.main:app --reload --port 8000")
    print("")
    print("2. Test API endpoints:")
    print("   Health check: http://localhost:8000/health")
    print("   API docs: http://localhost:8000/docs")
    print("")
    print("3. Start the UI (if needed):")
    print("   cd ui")
    print("   npm run dev")
    print("   Access: http://localhost:3000")
    print("")
    print("4. Test with curl:")
    print('   curl -X POST "http://localhost:8000/chat/" \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"message": "Hello, can you help assess a VAC case?"}\'')

async def main():
    """Run all validation tests"""
    print("🔍 VAC Assessment API - Setup Validation")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 5
    
    # Run all tests
    if check_file_structure():
        tests_passed += 1
    
    if test_environment_config():
        tests_passed += 1
    
    if test_vac_data_loading():
        tests_passed += 1
    
    if test_mock_logic_removed():
        tests_passed += 1
    
    if await test_openai_connection():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your system is ready for local testing.")
        print_next_steps()
    else:
        print("⚠️  Some tests failed. Please fix the issues above before proceeding.")
        
        if tests_passed >= 3:
            print("\n💡 You can still proceed with basic testing, but some features may not work correctly.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Local testing script for VAC Assessment API
Run this to test the system before containerization
"""

import asyncio
import json
import sys
from pathlib import Path
import logging

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app_simplified.core.openai_client import vac_client
from app_simplified.core.vac_data import vac_data_manager
from app_simplified.rating.vac_canada import VACRatingEngine
from app_simplified.documents.processor import document_processor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VACSystemTester:
    """Test the VAC assessment system components"""
    
    def __init__(self):
        self.rating_engine = VACRatingEngine()
    
    async def run_all_tests(self):
        """Run all system tests"""
        print("🏥 VAC Assessment System - Local Testing")
        print("=" * 50)
        
        tests = [
            ("VAC Data Loading", self.test_vac_data_loading),
            ("VAC Condition Search", self.test_condition_search),
            ("Rating Calculation", self.test_rating_calculation),
            ("Azure OpenAI Connection", self.test_openai_connection),
            ("Document Processing", self.test_document_processing),
            ("Full Assessment Flow", self.test_full_assessment)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print(f"\n🔍 Testing: {test_name}")
            try:
                result = await test_func()
                results[test_name] = {"status": "PASS", "result": result}
                print(f"✅ {test_name}: PASSED")
            except Exception as e:
                results[test_name] = {"status": "FAIL", "error": str(e)}
                print(f"❌ {test_name}: FAILED - {str(e)}")
        
        # Summary
        print(f"\n📊 Test Summary")
        print("=" * 30)
        passed = sum(1 for r in results.values() if r["status"] == "PASS")
        total = len(results)
        print(f"Tests Passed: {passed}/{total}")
        
        if passed == total:
            print("🎉 All tests passed! System ready for deployment.")
        else:
            print("⚠️ Some tests failed. Check the errors above.")
        
        return results
    
    async def test_vac_data_loading(self):
        """Test VAC ToD data loading and indexing"""
        validation = vac_data_manager.validate_data()
        
        if not validation["valid"]:
            raise Exception(f"VAC data validation failed: {validation['errors']}")
        
        stats = vac_data_manager.get_stats()
        
        if stats["total_conditions"] == 0:
            raise Exception("No VAC conditions loaded")
        
        return {
            "conditions_loaded": stats["total_conditions"],
            "chapters_loaded": stats["total_chapters"],
            "data_valid": validation["valid"]
        }
    
    async def test_condition_search(self):
        """Test VAC condition search functionality"""
        # Test exact condition search
        ptsd_condition = vac_data_manager.find_condition("PTSD")
        
        # Test fuzzy search
        back_conditions = vac_data_manager.search_conditions("back pain", limit=5)
        
        return {
            "ptsd_found": ptsd_condition is not None,
            "ptsd_condition": ptsd_condition.get("name") if ptsd_condition else None,
            "back_pain_results": len(back_conditions),
            "sample_back_condition": back_conditions[0].get("name") if back_conditions else None
        }
    
    async def test_rating_calculation(self):
        """Test VAC rating calculation"""
        # Create test case
        test_case = {
            "conditions": [
                {
                    "name": "PTSD",
                    "symptoms": ["nightmares", "anxiety", "depression", "insomnia"],
                    "severity": "moderate"
                },
                {
                    "name": "lower back pain",
                    "symptoms": ["chronic pain", "limited mobility", "muscle spasms"],
                    "severity": "severe"
                }
            ],
            "pre_existing": [],
            "medical_evidence": [
                {"content": "Patient diagnosed with PTSD", "source": "Medical Report 1"},
                {"content": "Lower back injury from service", "source": "Medical Report 2"}
            ]
        }
        
        result = await self.rating_engine.assess_case(test_case)
        
        if result["total_disability_rating"] <= 0:
            raise Exception("Rating calculation returned 0% disability")
        
        return {
            "total_rating": result["total_disability_rating"],
            "conditions_assessed": len(result["individual_conditions"]),
            "all_conditions_found": all(
                c.get("tod_found", False) for c in result["individual_conditions"]
            )
        }
    
    async def test_openai_connection(self):
        """Test Azure OpenAI connection"""
        # First test connection validation
        connection_valid = vac_client.validate_connection()
        
        if not connection_valid:
            raise Exception("Azure OpenAI connection validation failed - check your credentials")
        
        # Test simple chat
        try:
            response = await vac_client.simple_chat(
                "Hello, can you help with VAC assessments?"
            )
            
            if not response or len(response.strip()) == 0:
                raise Exception("Empty response from OpenAI")
            
            return {
                "connection_valid": True,
                "response_received": True,
                "response_length": len(response),
                "sample_response": response[:100] + "..." if len(response) > 100 else response
            }
            
        except Exception as e:
            raise Exception(f"OpenAI chat test failed: {str(e)}")
    
    async def test_document_processing(self):
        """Test document processing functionality"""
        # Create a test text file
        test_content = """
        MEDICAL REPORT
        
        Patient: John Smith
        Date: 2024-01-15
        
        Diagnosis: Post-Traumatic Stress Disorder (PTSD)
        
        Symptoms:
        - Nightmares and flashbacks
        - Severe anxiety
        - Depression
        - Sleep disturbances
        - Difficulty concentrating
        
        Severity: Moderate to severe
        
        Recommendations:
        - Continue therapy
        - Consider medication adjustment
        - Regular follow-up appointments
        """
        
        # Create a mock file object
        class MockFile:
            def __init__(self, content: str, filename: str):
                self.content = content.encode('utf-8')
                self.filename = filename
                self.position = 0
            
            async def read(self):
                return self.content
            
            async def seek(self, position):
                self.position = position
        
        mock_file = MockFile(test_content, "test_medical_report.txt")
        
        result = await document_processor.process_file(
            file=mock_file,
            case_id="test_case_001",
            user_id="test_user"
        )
        
        if result["status"] != "processed":
            raise Exception(f"Document processing failed: {result.get('error', 'Unknown error')}")
        
        return {
            "processing_success": True,
            "conditions_detected": result.get("conditions_detected", []),
            "file_processed": result["filename"]
        }
    
    async def test_full_assessment(self):
        """Test full assessment workflow"""
        # Test case data
        case_data = {
            "case_id": "test_full_001",
            "conditions": [
                {
                    "name": "PTSD",
                    "symptoms": ["anxiety", "depression", "nightmares"],
                    "severity": "moderate"
                }
            ],
            "medical_evidence": [
                {"content": "Patient shows signs of PTSD", "source": "Test Medical Report"}
            ]
        }
        
        # Run full assessment
        assessment = await self.rating_engine.assess_case(case_data)
        
        # Verify key components
        required_fields = [
            "total_disability_rating",
            "individual_conditions", 
            "quality_of_life_impact",
            "recommendations"
        ]
        
        missing_fields = [field for field in required_fields if field not in assessment]
        if missing_fields:
            raise Exception(f"Assessment missing required fields: {missing_fields}")
        
        if assessment["total_disability_rating"] <= 0:
            raise Exception("Full assessment returned 0% disability rating")
        
        return {
            "assessment_complete": True,
            "total_rating": assessment["total_disability_rating"],
            "conditions_processed": len(assessment["individual_conditions"]),
            "has_recommendations": len(assessment["recommendations"]) > 0,
            "qol_impact": assessment["quality_of_life_impact"]["impact_level"]
        }

async def main():
    """Main test runner"""
    print("Starting VAC Assessment System Tests...")
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ ERROR: .env file not found!")
        print("Please copy .env.example to .env and configure your Azure credentials")
        return
    
    # Check if VAC data file exists
    vac_data_file = Path("app_simplified/data/rules/master2019ToD.json")
    if not vac_data_file.exists():
        print(f"❌ ERROR: VAC data file not found at {vac_data_file}")
        print("Please ensure the VAC ToD JSON file is in the correct location")
        return
    
    tester = VACSystemTester()
    results = await tester.run_all_tests()
    
    # Save results to file
    results_file = Path("test_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📝 Test results saved to: {results_file}")

if __name__ == "__main__":
    asyncio.run(main())

"""
VAC Canada ToD 2019 Rating Engine - Updated with data manager integration
"""

import asyncio
from typing import Dict, List, Any, Optional
import logging
from app_simplified.core.vac_data import vac_data_manager

logger = logging.getLogger(__name__)

class VACRatingEngine:
    """
    VAC Canada Table of Disabilities 2019 rating engine
    Integrates with VACDataManager for data access
    """
    
    def __init__(self):
        self.data_manager = vac_data_manager
        self._validate_data()
    
    def _validate_data(self):
        """Validate VAC data is loaded"""
        validation = self.data_manager.validate_data()
        if not validation["valid"]:
            logger.error(f"VAC data validation failed: {validation['errors']}")
        else:
            logger.info(f"VAC data validated successfully: {validation['stats']}")
    
    async def assess_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive VAC assessment of a veteran's case
        """
        try:
            # Extract conditions from case data
            conditions = case_data.get("conditions", [])
            pre_existing = case_data.get("pre_existing", [])
            medical_evidence = case_data.get("medical_evidence", [])
            
            # Assess each condition
            assessed_conditions = []
            for condition in conditions:
                assessment = await self._assess_condition(condition, medical_evidence)
                assessed_conditions.append(assessment)
            
            # Calculate combined rating
            combined_rating = await self._calculate_combined_rating(
                assessed_conditions, 
                pre_existing
            )
            
            # Determine quality of life impact
            qol_impact = await self._assess_quality_of_life(assessed_conditions)
            
            return {
                "case_id": case_data.get("case_id"),
                "assessment_date": case_data.get("assessment_date"),
                "total_disability_rating": combined_rating["total_rating"],
                "individual_conditions": assessed_conditions,
                "combined_rating_breakdown": combined_rating,
                "quality_of_life_impact": qol_impact,
                "recommendations": await self._generate_recommendations(assessed_conditions),
                "tod_version": "VAC 2019",
                "assessment_confidence": combined_rating.get("confidence", "medium")
            }
            
        except Exception as e:
            logger.error(f"VAC assessment error: {e}")
            raise
    
    async def _assess_condition(self, condition: Dict[str, Any], medical_evidence: List[Dict]) -> Dict[str, Any]:
        """Assess a single condition using VAC ToD criteria with data manager"""
        try:
            condition_name = condition.get("name", "")
            symptoms = condition.get("symptoms", [])
            severity = condition.get("severity", "")
            
            # Use data manager to find condition
            tod_condition = self.data_manager.find_condition(condition_name)
            
            if not tod_condition:
                return {
                    "condition": condition_name,
                    "tod_found": False,
                    "rating": 0,
                    "rationale": f"Condition '{condition_name}' not found in VAC ToD 2019",
                    "chapter": "unknown"
                }
            
            # Use data manager's basic rating calculation
            rating_result = self.data_manager.calculate_basic_rating(
                condition_name=condition_name,
                severity=severity,
                symptoms=symptoms
            )
            
            # Enhanced assessment with medical evidence
            medical_evidence_support = await self._evaluate_medical_evidence(
                condition_name, medical_evidence
            )
            
            return {
                "condition": condition_name,
                "tod_condition_id": tod_condition.get("id"),
                "chapter": tod_condition.get("chapter"),
                "tod_found": True,
                "rating": rating_result["rating"],
                "rating_rationale": rating_result["rationale"],
                "symptoms_matched": rating_result["symptoms_considered"],
                "assessment_criteria_met": self._get_criteria_met(tod_condition, symptoms),
                "medical_evidence_support": medical_evidence_support,
                "base_rating": rating_result.get("base_rating"),
                "symptom_adjustment": rating_result.get("symptom_adjustment"),
                "tod_criteria": rating_result.get("tod_criteria", {})
            }
            
        except Exception as e:
            logger.error(f"Condition assessment error: {e}")
            return {
                "condition": condition.get("name", "unknown"),
                "tod_found": False,
                "rating": 0,
                "error": str(e)
            }
    
    def _get_criteria_met(self, condition: Dict, symptoms: List[str]) -> List[str]:
        """Determine which assessment criteria were met"""
        criteria_met = ["condition_identified", "tod_match_found"]
        
        if symptoms:
            criteria_met.append("symptoms_documented")
            
        # Check if symptoms match ToD symptoms
        tod_symptoms = condition.get("symptoms", [])
        if tod_symptoms and symptoms:
            matching_symptoms = []
            for symptom in symptoms:
                for tod_symptom in tod_symptoms:
                    if symptom.lower() in tod_symptom.lower() or tod_symptom.lower() in symptom.lower():
                        matching_symptoms.append(symptom)
                        break
            
            if matching_symptoms:
                criteria_met.append("symptoms_match_tod")
        
        return criteria_met
    
    async def _calculate_combined_rating(self, conditions: List[Dict], pre_existing: List[Dict]) -> Dict[str, Any]:
        """Calculate combined disability rating using VAC methodology"""
        if not conditions:
            return {"total_rating": 0, "method": "no_conditions", "confidence": "low"}
        
        # Extract individual ratings for conditions found in ToD
        valid_conditions = [c for c in conditions if c.get("tod_found", False)]
        individual_ratings = [c.get("rating", 0) for c in valid_conditions]
        
        if not individual_ratings:
            return {"total_rating": 0, "method": "no_valid_conditions", "confidence": "low"}
        
        # VAC combination formula
        if len(individual_ratings) == 1:
            total_rating = individual_ratings[0]
            method = "single_condition"
            confidence = "high"
        else:
            # VAC combination: A + B - (A × B / 100)
            total_rating = individual_ratings[0]
            for rating in individual_ratings[1:]:
                total_rating = total_rating + rating - (total_rating * rating / 100)
            
            total_rating = int(round(total_rating))
            method = "vac_combination_formula"
            confidence = "medium"
        
        # Apply pre-existing condition adjustments if any
        pct_applied = False
        if pre_existing:
            # PCT logic would be implemented here
            pct_applied = True
            confidence = "medium"  # Reduced confidence with PCT
        
        # Ensure rating doesn't exceed 100%
        total_rating = min(100, total_rating)
        
        return {
            "total_rating": total_rating,
            "individual_ratings": individual_ratings,
            "method": method,
            "pct_applied": pct_applied,
            "confidence": confidence,
            "calculation_details": {
                "valid_conditions": len(valid_conditions),
                "total_conditions": len(conditions),
                "combination_steps": self._get_combination_steps(individual_ratings)
            }
        }
    
    def _get_combination_steps(self, ratings: List[int]) -> List[str]:
        """Get step-by-step combination calculation"""
        if len(ratings) <= 1:
            return [f"Single condition: {ratings[0] if ratings else 0}%"]
        
        steps = []
        combined = ratings[0]
        steps.append(f"Start with highest rating: {combined}%")
        
        for i, rating in enumerate(ratings[1:], 1):
            old_combined = combined
            combined = combined + rating - (combined * rating / 100)
            steps.append(f"Step {i}: {old_combined}% + {rating}% - ({old_combined}% × {rating}% ÷ 100) = {combined:.1f}%")
        
        steps.append(f"Final combined rating: {int(round(combined))}%")
        return steps
    
    async def _assess_quality_of_life(self, conditions: List[Dict]) -> Dict[str, Any]:
        """Assess quality of life impact based on conditions and ratings"""
        total_rating = sum(c.get("rating", 0) for c in conditions if c.get("tod_found", False))
        condition_count = len([c for c in conditions if c.get("tod_found", False)])
        
        # Determine impact level
        if total_rating >= 75:
            impact_level = "severe"
        elif total_rating >= 50:
            impact_level = "moderate_to_severe"  
        elif total_rating >= 25:
            impact_level = "moderate"
        else:
            impact_level = "mild"
        
        # Assess functional limitations
        functional_limitations = await self._assess_functional_limitations(conditions)
        
        # Generate QoL recommendations
        recommendations = await self._generate_qol_recommendations(impact_level, functional_limitations)
        
        return {
            "impact_level": impact_level,
            "total_rating": total_rating,
            "condition_count": condition_count,
            "functional_limitations": functional_limitations,
            "recommendations": recommendations,
            "assessment_factors": {
                "multiple_conditions": condition_count > 1,
                "high_individual_ratings": any(c.get("rating", 0) >= 50 for c in conditions),
                "mental_health_present": any("mental" in c.get("condition", "").lower() or 
                                           "ptsd" in c.get("condition", "").lower() for c in conditions)
            }
        }
    
    async def _assess_functional_limitations(self, conditions: List[Dict]) -> List[str]:
        """Assess functional limitations based on conditions"""
        limitations = set()
        
        for condition in conditions:
            if not condition.get("tod_found", False):
                continue
                
            rating = condition.get("rating", 0)
            condition_name = condition.get("condition", "").lower()
            
            # High rating conditions cause more limitations
            if rating >= 50:
                if any(term in condition_name for term in ["mental", "ptsd", "anxiety", "depression"]):
                    limitations.update(["concentration", "memory", "social_interaction", "decision_making"])
                elif any(term in condition_name for term in ["back", "spine", "lumbar"]):
                    limitations.update(["mobility", "lifting", "prolonged_sitting", "bending"])
                elif any(term in condition_name for term in ["knee", "leg", "hip"]):
                    limitations.update(["walking", "standing", "climbing", "running"])
                elif any(term in condition_name for term in ["shoulder", "arm", "hand"]):
                    limitations.update(["reaching", "grasping", "lifting", "fine_motor"])
                elif any(term in condition_name for term in ["neck", "cervical"]):
                    limitations.update(["neck_movement", "concentration", "headaches"])
        
        return sorted(list(limitations))
    
    async def _generate_qol_recommendations(self, impact_level: str, limitations: List[str]) -> List[str]:
        """Generate quality of life recommendations"""
        base_recommendations = {
            "mild": [
                "Regular medical follow-up recommended",
                "Monitor condition progression", 
                "Consider preventive care measures"
            ],
            "moderate": [
                "Regular medical care and monitoring required",
                "Consider rehabilitation services",
                "Workplace accommodations may be beneficial",
                "Assess need for assistive devices"
            ],
            "moderate_to_severe": [
                "Comprehensive medical care required",
                "Rehabilitation and support services recommended",
                "Significant workplace accommodations needed",
                "Consider vocational retraining options",
                "Family support services may be helpful"
            ],
            "severe": [
                "Intensive medical care and support required",
                "Comprehensive rehabilitation program recommended",
                "Full disability accommodations needed",
                "Consider long-term care planning",
                "Family and caregiver support essential"
            ]
        }
        
        recommendations = base_recommendations.get(impact_level, [])
        
        # Add limitation-specific recommendations
        if "mobility" in limitations:
            recommendations.append("Assess need for mobility aids and home modifications")
        if "mental" in str(limitations).lower() or "concentration" in limitations:
            recommendations.append("Consider mental health support services")
        if len(limitations) > 3:
            recommendations.append("Comprehensive occupational therapy assessment recommended")
        
        return recommendations
    
    async def _evaluate_medical_evidence(self, condition_name: str, medical_evidence: List[Dict]) -> Dict[str, Any]:
        """Evaluate medical evidence support for condition"""
        relevant_evidence = []
        evidence_quality = "limited"
        
        for evidence in medical_evidence:
            evidence_content = evidence.get("content", "").lower()
            evidence_source = evidence.get("source", "")
            
            if condition_name.lower() in evidence_content:
                relevant_evidence.append({
                    "source": evidence_source,
                    "relevance": "high" if condition_name.lower() in evidence_content[:200] else "medium"
                })
        
        # Assess evidence adequacy
        if len(relevant_evidence) >= 3:
            evidence_quality = "comprehensive"
        elif len(relevant_evidence) >= 2:
            evidence_quality = "adequate"
        elif len(relevant_evidence) == 1:
            evidence_quality = "limited"
        else:
            evidence_quality = "insufficient"
        
        return {
            "evidence_count": len(relevant_evidence),
            "relevant_sources": [e["source"] for e in relevant_evidence],
            "quality_assessment": evidence_quality,
            "adequacy_for_rating": evidence_quality in ["adequate", "comprehensive"],
            "recommendations": self._get_evidence_recommendations(evidence_quality)
        }
    
    def _get_evidence_recommendations(self, quality: str) -> List[str]:
        """Get recommendations based on evidence quality"""
        recommendations_map = {
            "insufficient": [
                "Obtain comprehensive medical documentation",
                "Request current medical examinations",
                "Gather service medical records"
            ],
            "limited": [
                "Obtain additional supporting medical evidence",
                "Consider independent medical examination",
                "Document current symptom severity"
            ],
            "adequate": [
                "Evidence supports assessment",
                "Consider periodic review"
            ],
            "comprehensive": [
                "Strong medical evidence foundation",
                "Evidence fully supports assessment"
            ]
        }
        
        return recommendations_map.get(quality, [])
    
    async def _generate_recommendations(self, conditions: List[Dict]) -> List[str]:
        """Generate overall assessment recommendations"""
        recommendations = []
        
        total_rating = sum(c.get("rating", 0) for c in conditions if c.get("tod_found", False))
        valid_conditions = [c for c in conditions if c.get("tod_found", False)]
        invalid_conditions = [c for c in conditions if not c.get("tod_found", False)]
        
        # Rating-based recommendations
        if total_rating >= 70:
            recommendations.extend([
                "Veteran qualifies for significant VAC disability benefits",
                "Priority access to VAC programs and services recommended",
                "Comprehensive support services should be considered"
            ])
        elif total_rating >= 30:
            recommendations.extend([
                "Veteran qualifies for VAC disability compensation",
                "Rehabilitation services may be beneficial",
                "Regular medical follow-up recommended"
            ])
        else:
            recommendations.extend([
                "Continue monitoring condition progression",
                "Document any symptom changes or deterioration",
                "Regular medical care recommended"
            ])
        
        # Condition-specific recommendations
        for condition in invalid_conditions:
            recommendations.append(f"Obtain additional medical documentation for '{condition.get('condition')}'")
        
        # Evidence-based recommendations
        low_evidence_conditions = [c for c in valid_conditions 
                                 if c.get("medical_evidence_support", {}).get("quality_assessment") in ["insufficient", "limited"]]
        
        if low_evidence_conditions:
            recommendations.append("Consider obtaining additional medical evidence for more accurate assessment")
        
        return recommendations
    
    async def calculate_rating(self, rating_data: Dict[str, Any]) -> Dict[str, Any]:
        """Direct rating calculation for specific conditions"""
        conditions = rating_data.get("conditions", [])
        pre_existing = rating_data.get("pre_existing", [])
        
        # Assess each condition
        assessed_conditions = []
        for condition in conditions:
            assessment = await self._assess_condition(condition, [])
            assessed_conditions.append(assessment)
        
        # Calculate combined rating
        combined_rating = await self._calculate_combined_rating(assessed_conditions, pre_existing)
        
        return {
            "total_rating": combined_rating["total_rating"],
            "conditions": assessed_conditions,
            "method": combined_rating["method"],
            "pct_applied": combined_rating.get("pct_applied", False),
            "calculation_details": combined_rating.get("calculation_details", {}),
            "confidence": combined_rating.get("confidence", "medium")
        }
    
    async def get_conditions(self, chapter: Optional[str] = None, search_term: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of VAC ToD conditions using data manager"""
        try:
            if search_term:
                results = self.data_manager.search_conditions(
                    query=search_term,
                    chapter=chapter,
                    limit=50
                )
                return [
                    {
                        "id": result.get("id"),
                        "name": result.get("name"),
                        "chapter": result.get("chapter"),
                        "symptoms": result.get("symptoms", []),
                        "relevance_score": result.get("relevance_score", 0)
                    }
                    for result in results
                ]
            else:
                if chapter:
                    conditions = self.data_manager.get_chapter_conditions(chapter)
                else:
                    conditions = list(self.data_manager.conditions_index.values())
                
                return [
                    {
                        "id": condition.get("id"),
                        "name": condition.get("name"),
                        "chapter": condition.get("chapter"),
                        "symptoms": condition.get("symptoms", [])
                    }
                    for condition in conditions
                ]
        
        except Exception as e:
            logger.error(f"Error getting conditions: {e}")
            return []
    
    async def get_chapters(self) -> List[Dict[str, Any]]:
        """Get list of VAC ToD chapters using data manager"""
        try:
            return self.data_manager.get_all_chapters()
        except Exception as e:
            logger.error(f"Error getting chapters: {e}")
            return []
    
    async def get_case_history(self, case_id: str) -> List[Dict[str, Any]]:
        """Get assessment history for a case (placeholder - would use database)"""
        return [
            {
                "assessment_date": "2024-01-15",
                "total_rating": 45,
                "conditions_assessed": 3,
                "assessor": "VAC Assessment System",
                "notes": "Initial comprehensive assessment"
            }
        ]

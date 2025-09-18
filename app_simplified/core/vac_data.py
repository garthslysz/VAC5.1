"""
VAC Table of Disabilities 2019 data processing and management
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from fuzzywuzzy import fuzz, process
import re

logger = logging.getLogger(__name__)

class VACDataManager:
    """
    Manages VAC Table of Disabilities 2019 data
    Provides search, lookup, and indexing functionality
    """
    
    def __init__(self, json_path: Optional[str] = None):
        self.json_path = json_path or "app_simplified/data/rules/master2019ToD.json"
        self.tod_data = {}
        self.conditions_index = {}
        self.chapters_index = {}
        self.rating_tables = {}
        self.search_index = {}
        
        self._load_tod_data()
        self._build_indexes()
    
    def _load_tod_data(self) -> bool:
        """Load VAC ToD 2019 JSON data"""
        try:
            tod_path = Path(self.json_path)
            
            if not tod_path.exists():
                logger.error(f"VAC ToD data file not found: {tod_path}")
                return False
            
            with open(tod_path, 'r', encoding='utf-8') as f:
                self.tod_data = json.load(f)
            
            logger.info(f"VAC ToD 2019 data loaded from {tod_path}")
            logger.info(f"Data structure keys: {list(self.tod_data.keys()) if self.tod_data else 'Empty'}")
            
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in VAC ToD file: {e}")
            return False
        except Exception as e:
            logger.error(f"Error loading VAC ToD data: {e}")
            return False
    
    def _build_indexes(self):
        """Build search indexes for fast lookup"""
        if not self.tod_data:
            logger.warning("No VAC ToD data to index")
            return
        
        try:
            # Index chapters
            chapters_data = self.tod_data.get("chapters", {})
            for chapter_id, chapter_info in chapters_data.items():
                self.chapters_index[chapter_id] = {
                    "id": chapter_id,
                    "title": chapter_info.get("title", ""),
                    "description": chapter_info.get("description", ""),
                    "conditions": chapter_info.get("conditions", []),
                    "sections": chapter_info.get("sections", [])
                }
            
            # Index conditions
            conditions_data = self.tod_data.get("conditions", {})
            for condition_id, condition_info in conditions_data.items():
                self.conditions_index[condition_id] = {
                    "id": condition_id,
                    "name": condition_info.get("name", ""),
                    "chapter": condition_info.get("chapter", ""),
                    "description": condition_info.get("description", ""),
                    "symptoms": condition_info.get("symptoms", []),
                    "rating_criteria": condition_info.get("rating_criteria", {}),
                    "assessment_notes": condition_info.get("assessment_notes", ""),
                    "keywords": condition_info.get("keywords", [])
                }
            
            # Index rating tables
            rating_tables_data = self.tod_data.get("rating_tables", {})
            for table_id, table_info in rating_tables_data.items():
                self.rating_tables[table_id] = table_info
            
            # Build search index for fuzzy matching
            self._build_search_index()
            
            logger.info(f"Built indexes: {len(self.chapters_index)} chapters, "
                       f"{len(self.conditions_index)} conditions, "
                       f"{len(self.rating_tables)} rating tables")
            
        except Exception as e:
            logger.error(f"Error building VAC ToD indexes: {e}")
    
    def _build_search_index(self):
        """Build full-text search index"""
        self.search_index = {}
        
        # Index condition names and synonyms for fuzzy search
        for condition_id, condition in self.conditions_index.items():
            search_terms = [
                condition["name"],
                condition.get("description", ""),
            ]
            
            # Add keywords
            search_terms.extend(condition.get("keywords", []))
            
            # Add symptoms as searchable terms
            search_terms.extend(condition.get("symptoms", []))
            
            # Clean and store
            cleaned_terms = [term.lower().strip() for term in search_terms if term]
            self.search_index[condition_id] = {
                "condition": condition,
                "search_terms": cleaned_terms,
                "primary_name": condition["name"].lower()
            }
    
    def find_condition(self, condition_name: str, threshold: int = 70) -> Optional[Dict[str, Any]]:
        """
        Find VAC ToD condition using fuzzy matching
        
        Args:
            condition_name: Name of condition to find
            threshold: Minimum similarity threshold (0-100)
            
        Returns:
            Best matching condition info or None
        """
        if not condition_name or not self.search_index:
            return None
        
        condition_name = condition_name.lower().strip()
        best_match = None
        best_score = 0
        
        for condition_id, index_data in self.search_index.items():
            # Check primary name first
            primary_score = fuzz.ratio(condition_name, index_data["primary_name"])
            if primary_score > best_score:
                best_score = primary_score
                best_match = index_data["condition"]
            
            # Check all search terms
            for term in index_data["search_terms"]:
                if not term:
                    continue
                    
                # Exact match gets priority
                if condition_name == term:
                    return index_data["condition"]
                
                # Partial ratio for partial matches
                score = max(
                    fuzz.ratio(condition_name, term),
                    fuzz.partial_ratio(condition_name, term),
                    fuzz.token_sort_ratio(condition_name, term)
                )
                
                if score > best_score:
                    best_score = score
                    best_match = index_data["condition"]
        
        if best_score >= threshold:
            logger.info(f"Found condition match: '{condition_name}' -> '{best_match['name']}' (score: {best_score})")
            return best_match
        
        logger.warning(f"No condition match found for '{condition_name}' (best score: {best_score})")
        return None
    
    def get_condition_by_id(self, condition_id: str) -> Optional[Dict[str, Any]]:
        """Get condition by exact ID"""
        return self.conditions_index.get(condition_id)
    
    def get_chapter_conditions(self, chapter_id: str) -> List[Dict[str, Any]]:
        """Get all conditions in a specific chapter"""
        conditions = []
        for condition in self.conditions_index.values():
            if condition.get("chapter") == chapter_id:
                conditions.append(condition)
        
        return sorted(conditions, key=lambda x: x.get("name", ""))
    
    def search_conditions(
        self, 
        query: str, 
        chapter: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search conditions by query string
        
        Args:
            query: Search query
            chapter: Filter by chapter
            limit: Maximum results to return
            
        Returns:
            List of matching conditions with similarity scores
        """
        if not query:
            return []
        
        results = []
        query_lower = query.lower().strip()
        
        for condition in self.conditions_index.values():
            # Filter by chapter if specified
            if chapter and condition.get("chapter") != chapter:
                continue
            
            # Calculate relevance score
            name_score = fuzz.partial_ratio(query_lower, condition.get("name", "").lower())
            desc_score = fuzz.partial_ratio(query_lower, condition.get("description", "").lower())
            
            # Check symptoms
            symptom_scores = []
            for symptom in condition.get("symptoms", []):
                symptom_scores.append(fuzz.partial_ratio(query_lower, symptom.lower()))
            
            max_symptom_score = max(symptom_scores) if symptom_scores else 0
            
            # Overall relevance score
            relevance = max(name_score, desc_score, max_symptom_score)
            
            if relevance > 50:  # Threshold for inclusion
                results.append({
                    **condition,
                    "relevance_score": relevance
                })
        
        # Sort by relevance and limit results
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:limit]
    
    def get_all_chapters(self) -> List[Dict[str, Any]]:
        """Get all VAC ToD chapters"""
        chapters = []
        for chapter in self.chapters_index.values():
            chapter_info = dict(chapter)
            chapter_info["condition_count"] = len(self.get_chapter_conditions(chapter["id"]))
            chapters.append(chapter_info)
        
        return sorted(chapters, key=lambda x: x.get("id", ""))
    
    def get_rating_table(self, table_id: str) -> Optional[Dict[str, Any]]:
        """Get rating table by ID"""
        return self.rating_tables.get(table_id)
    
    def get_condition_rating_info(self, condition_id: str) -> Optional[Dict[str, Any]]:
        """Get rating information for a specific condition"""
        condition = self.get_condition_by_id(condition_id)
        if not condition:
            return None
        
        rating_info = {
            "condition": condition,
            "rating_criteria": condition.get("rating_criteria", {}),
            "tables": []
        }
        
        # Look up associated rating tables
        rating_criteria = condition.get("rating_criteria", {})
        for table_ref in rating_criteria.get("tables", []):
            table = self.get_rating_table(table_ref)
            if table:
                rating_info["tables"].append(table)
        
        return rating_info
    
    def calculate_basic_rating(
        self, 
        condition_name: str, 
        severity: str, 
        symptoms: List[str]
    ) -> Dict[str, Any]:
        """
        Calculate basic disability rating for a condition
        Note: This is a simplified implementation for testing
        Real VAC calculations are much more complex
        """
        condition = self.find_condition(condition_name)
        
        if not condition:
            return {
                "condition": condition_name,
                "found": False,
                "rating": 0,
                "rationale": f"Condition '{condition_name}' not found in VAC ToD 2019"
            }
        
        # Simple severity-based rating (placeholder logic)
        severity_ratings = {
            "minimal": 5,
            "mild": 10,
            "moderate": 30,
            "moderately_severe": 50,
            "severe": 70,
            "very_severe": 90,
            "total": 100
        }
        
        base_rating = severity_ratings.get(severity.lower(), 20)
        
        # Adjust for number of symptoms (simplified)
        symptom_adjustment = min(len(symptoms) * 2, 20)
        final_rating = min(base_rating + symptom_adjustment, 100)
        
        return {
            "condition": condition["name"],
            "condition_id": condition["id"],
            "chapter": condition.get("chapter", ""),
            "found": True,
            "rating": final_rating,
            "base_rating": base_rating,
            "symptom_adjustment": symptom_adjustment,
            "rationale": f"Base rating {base_rating}% for {severity} severity, "
                        f"adjusted +{symptom_adjustment}% for {len(symptoms)} symptoms",
            "symptoms_considered": symptoms,
            "tod_criteria": condition.get("rating_criteria", {})
        }
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about loaded VAC ToD data"""
        return {
            "total_chapters": len(self.chapters_index),
            "total_conditions": len(self.conditions_index),
            "total_rating_tables": len(self.rating_tables),
            "search_index_size": len(self.search_index)
        }
    
    def validate_data(self) -> Dict[str, Any]:
        """Validate loaded VAC ToD data structure"""
        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "stats": self.get_stats()
        }
        
        # Check if data was loaded
        if not self.tod_data:
            validation["valid"] = False
            validation["errors"].append("No VAC ToD data loaded")
            return validation
        
        # Check required sections
        required_sections = ["chapters"]  # Made conditions optional for demo
        for section in required_sections:
            if section not in self.tod_data:
                validation["errors"].append(f"Missing required section: {section}")
                validation["valid"] = False
        
        # Check for optional sections and warn if missing
        if "conditions" not in self.tod_data:
            validation["warnings"].append("No conditions section found - using chapter-based routing only")
        
        # Check for empty indexes
        if not self.conditions_index:
            validation["warnings"].append("No conditions found in data")
        
        if not self.chapters_index:
            validation["warnings"].append("No chapters found in data")
        
        return validation

# Global instance for application use
vac_data_manager = VACDataManager()

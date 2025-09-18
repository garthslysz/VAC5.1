"""
Document search functionality for VAC assessments
"""

import logging
from typing import Dict, List, Any, Optional
from app_simplified.core.vac_data import vac_data_manager
from app_simplified.documents.processor import document_processor

logger = logging.getLogger(__name__)

class DocumentSearch:
    """
    Search functionality for VAC documents and uploaded files
    Combines VAC ToD search with uploaded document search
    """
    
    def __init__(self):
        self.vac_data = vac_data_manager
        self.doc_processor = document_processor
    
    async def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search across VAC ToD documents and uploaded files
        
        Args:
            query: Search query
            filters: Optional filters (jurisdiction, chapter, etc.)
            limit: Maximum results to return
            
        Returns:
            Combined search results from VAC ToD and uploaded documents
        """
        try:
            results = []
            
            # Search VAC ToD data
            vac_results = await self._search_vac_tod(query, filters, limit // 2)
            results.extend(vac_results)
            
            # Search uploaded documents
            doc_results = await self._search_uploaded_documents(query, filters, limit // 2)
            results.extend(doc_results)
            
            # Sort by relevance score
            results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Document search error: {e}")
            return []
    
    async def _search_vac_tod(
        self,
        query: str,
        filters: Optional[Dict[str, Any]],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Search VAC Table of Disabilities"""
        try:
            chapter = filters.get("chapter") if filters else None
            
            conditions = self.vac_data.search_conditions(
                query=query,
                chapter=chapter,
                limit=limit
            )
            
            results = []
            for condition in conditions:
                results.append({
                    "id": f"vac_tod_{condition.get('id')}",
                    "title": condition.get("name", ""),
                    "content": condition.get("description", ""),
                    "source": "VAC Table of Disabilities 2019",
                    "chapter": condition.get("chapter", ""),
                    "document_type": "tod_condition",
                    "relevance_score": condition.get("relevance_score", 0) / 100,  # Normalize to 0-1
                    "metadata": {
                        "condition_id": condition.get("id"),
                        "symptoms": condition.get("symptoms", []),
                        "rating_criteria": condition.get("rating_criteria", {})
                    }
                })
            
            return results
            
        except Exception as e:
            logger.error(f"VAC ToD search error: {e}")
            return []
    
    async def _search_uploaded_documents(
        self,
        query: str,
        filters: Optional[Dict[str, Any]],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Search uploaded documents"""
        try:
            results = []
            query_lower = query.lower()
            
            # Search through processed files
            for file_id, file_info in self.doc_processor.processed_files.items():
                if file_info.get("status") != "processed":
                    continue
                
                extracted_text = file_info.get("extracted_text", "")
                if not extracted_text:
                    continue
                
                # Simple text search
                text_lower = extracted_text.lower()
                
                # Calculate relevance score
                relevance_score = 0
                query_words = query_lower.split()
                
                for word in query_words:
                    if word in text_lower:
                        # Count occurrences
                        word_count = text_lower.count(word)
                        relevance_score += word_count
                
                if relevance_score > 0:
                    # Normalize score based on document length
                    normalized_score = min(relevance_score / len(query_words), 1.0)
                    
                    # Find relevant excerpts
                    excerpts = self._extract_relevant_excerpts(extracted_text, query_words, max_excerpts=2)
                    
                    results.append({
                        "id": f"uploaded_{file_id}",
                        "title": file_info.get("filename", ""),
                        "content": " ... ".join(excerpts),
                        "source": f"Uploaded Document: {file_info.get('filename')}",
                        "document_type": "uploaded_document",
                        "relevance_score": normalized_score,
                        "metadata": {
                            "file_id": file_id,
                            "file_type": file_info.get("file_type", ""),
                            "processed_at": file_info.get("processed_at", ""),
                            "case_id": file_info.get("case_id"),
                            "medical_analysis": file_info.get("medical_analysis", {})
                        }
                    })
            
            # Sort by relevance and limit
            results.sort(key=lambda x: x["relevance_score"], reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Uploaded documents search error: {e}")
            return []
    
    def _extract_relevant_excerpts(
        self,
        text: str,
        query_words: List[str],
        max_excerpts: int = 2,
        excerpt_length: int = 150
    ) -> List[str]:
        """Extract relevant text excerpts containing query words"""
        excerpts = []
        text_lower = text.lower()
        
        for word in query_words:
            word_positions = []
            start = 0
            
            # Find all occurrences of the word
            while True:
                pos = text_lower.find(word, start)
                if pos == -1:
                    break
                word_positions.append(pos)
                start = pos + 1
            
            # Extract excerpts around word positions
            for pos in word_positions[:max_excerpts]:
                start_pos = max(0, pos - excerpt_length // 2)
                end_pos = min(len(text), pos + excerpt_length // 2)
                
                excerpt = text[start_pos:end_pos].strip()
                if excerpt and excerpt not in excerpts:
                    excerpts.append(excerpt)
                
                if len(excerpts) >= max_excerpts:
                    break
            
            if len(excerpts) >= max_excerpts:
                break
        
        return excerpts
    
    async def search_by_condition(
        self,
        condition_name: str,
        case_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for information about a specific condition
        
        Args:
            condition_name: Name of medical condition
            case_id: Optional case ID to include case-specific documents
            
        Returns:
            Comprehensive information about the condition
        """
        try:
            # Find VAC ToD condition
            vac_condition = self.vac_data.find_condition(condition_name)
            
            # Search for related information
            search_results = await self.search(
                query=condition_name,
                filters={"condition_type": "medical"} if case_id else None,
                limit=20
            )
            
            # Get case-specific files if case_id provided
            case_files = []
            if case_id:
                case_files = await self.doc_processor.get_case_files(case_id)
                # Filter for files that mention this condition
                case_files = [
                    f for f in case_files
                    if condition_name.lower() in str(f.get("conditions_detected", [])).lower()
                ]
            
            return {
                "condition_name": condition_name,
                "vac_tod_match": vac_condition,
                "search_results": search_results,
                "case_specific_files": case_files,
                "total_results": len(search_results),
                "found_in_tod": vac_condition is not None,
                "evidence_strength": self._assess_evidence_strength(search_results, case_files)
            }
            
        except Exception as e:
            logger.error(f"Condition search error for '{condition_name}': {e}")
            return {
                "condition_name": condition_name,
                "error": str(e),
                "search_results": [],
                "case_specific_files": []
            }
    
    def _assess_evidence_strength(
        self,
        search_results: List[Dict],
        case_files: List[Dict]
    ) -> str:
        """Assess the strength of available evidence"""
        
        tod_results = len([r for r in search_results if r.get("document_type") == "tod_condition"])
        uploaded_results = len([r for r in search_results if r.get("document_type") == "uploaded_document"])
        
        if tod_results > 0 and len(case_files) > 2:
            return "strong"
        elif tod_results > 0 and len(case_files) > 0:
            return "moderate"
        elif tod_results > 0 or len(case_files) > 1:
            return "limited"
        else:
            return "insufficient"
    
    async def get_chapter_contents(self, chapter_id: str) -> Dict[str, Any]:
        """Get all contents for a specific VAC ToD chapter"""
        try:
            chapter_info = self.vac_data.chapters_index.get(chapter_id)
            if not chapter_info:
                return {"error": f"Chapter {chapter_id} not found"}
            
            conditions = self.vac_data.get_chapter_conditions(chapter_id)
            
            return {
                "chapter": chapter_info,
                "conditions": conditions,
                "condition_count": len(conditions)
            }
            
        except Exception as e:
            logger.error(f"Error getting chapter contents for {chapter_id}: {e}")
            return {"error": str(e)}
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get search statistics"""
        try:
            return {
                "vac_tod_conditions": len(self.vac_data.conditions_index),
                "vac_tod_chapters": len(self.vac_data.chapters_index),
                "uploaded_documents": len(self.doc_processor.processed_files),
                "searchable_documents": len([
                    f for f in self.doc_processor.processed_files.values()
                    if f.get("status") == "processed"
                ])
            }
        except Exception as e:
            logger.error(f"Error getting search stats: {e}")
            return {}

# Global instance for application use
document_search = DocumentSearch()

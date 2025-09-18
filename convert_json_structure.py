#!/usr/bin/env python3
"""
Convert VAC ToD JSON from chapter-based structure to flat structure
expected by the VAC data loader.

This script preserves ALL adjudication data while restructuring it.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

def extract_conditions_from_chapters(chapters: Dict[str, Any]) -> Dict[str, Any]:
    """Extract condition-like entries from chapter data"""
    conditions = {}

    for chapter_id, chapter_data in chapters.items():
        chapter_title = chapter_data.get("title", f"Chapter {chapter_id}")

        # Look for tables that might contain conditions
        tables = chapter_data.get("tables", {})

        for table_id, table_data in tables.items():
            # Create a condition entry based on table
            condition_id = f"{chapter_id}_{table_id}"

            # Extract meaningful condition name
            condition_name = table_data.get("title", table_id.replace("_", " ").title())

            # For musculoskeletal conditions, create specific condition names
            if chapter_id == "17" and "spine" in table_id.lower():
                if "ROM" in table_id:
                    condition_name = "Spine Range of Motion Impairment"
                elif "back" in table_id.lower():
                    condition_name = "Back Pain and Spine Disorders"

            # Create condition entry
            conditions[condition_id] = {
                "id": condition_id,
                "name": condition_name,
                "chapter": chapter_id,
                "chapter_title": chapter_title,
                "description": f"Condition from {chapter_title}",
                "table_reference": table_id,
                "symptoms": [],
                "rating_criteria": table_data,
                "assessment_notes": f"Refer to Chapter {chapter_id}: {chapter_title}",
                "keywords": [
                    condition_name.lower(),
                    table_id.lower().replace("_", " "),
                    chapter_title.lower()
                ],
                "source_table": table_data
            }

            # Add specific keywords for spine/back conditions
            if chapter_id == "17":
                conditions[condition_id]["keywords"].extend([
                    "spine", "back", "musculoskeletal", "msk", "vertebral"
                ])

                if "spine" in table_id.lower():
                    conditions[condition_id]["keywords"].extend([
                        "chronic back pain", "low back pain", "spine pain",
                        "vertebral", "lumbar", "thoracic", "cervical"
                    ])

    return conditions

def extract_rating_tables_from_chapters(chapters: Dict[str, Any]) -> Dict[str, Any]:
    """Extract rating tables from chapter data"""
    rating_tables = {}

    for chapter_id, chapter_data in chapters.items():
        tables = chapter_data.get("tables", {})

        for table_id, table_data in tables.items():
            # Use full table reference as key
            full_table_id = f"{chapter_id}.{table_id}"

            # Preserve the original table structure
            rating_tables[full_table_id] = {
                "id": full_table_id,
                "chapter": chapter_id,
                "chapter_title": chapter_data.get("title", f"Chapter {chapter_id}"),
                "table_id": table_id,
                "title": table_data.get("title", table_id),
                "data": table_data,
                **table_data  # Include all original table data
            }

    return rating_tables

def convert_json_structure(input_file: Path, output_file: Path):
    """Convert JSON from chapter structure to flat structure"""

    print(f"Loading original JSON from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        original_data = json.load(f)

    # Preserve original metadata
    converted_data = {
        "schema_version": original_data.get("schema_version", "0.4.0"),
        "source": original_data.get("source", {}),
        "metadata": original_data.get("metadata", {}),
        "validation": original_data.get("validation", {}),
        "global": original_data.get("global", {}),
        "overall_directions": original_data.get("overall_directions", {}),
    }

    # Get chapters data
    chapters = original_data.get("chapters", {})

    print(f"Processing {len(chapters)} chapters...")

    # Convert to flat structure
    converted_data["conditions"] = extract_conditions_from_chapters(chapters)
    converted_data["rating_tables"] = extract_rating_tables_from_chapters(chapters)

    # Preserve original chapters for reference
    converted_data["chapters"] = chapters
    converted_data["path_index"] = original_data.get("path_index", {})

    # Add conversion metadata
    converted_data["conversion_info"] = {
        "converted_from": "chapter_based_structure",
        "conversion_timestamp": "2025-09-18",
        "original_chapters": len(chapters),
        "extracted_conditions": len(converted_data["conditions"]),
        "extracted_rating_tables": len(converted_data["rating_tables"]),
        "note": "All original chapter data preserved. Conditions and rating_tables extracted for flat access."
    }

    print(f"Extracted {len(converted_data['conditions'])} conditions")
    print(f"Extracted {len(converted_data['rating_tables'])} rating tables")

    # Write converted file
    print(f"Writing converted JSON to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted_data, f, indent=2, ensure_ascii=False)

    print("✅ Conversion completed successfully!")

    # Show some examples
    print("\n📋 Sample conditions created:")
    for i, (cond_id, cond_data) in enumerate(converted_data["conditions"].items()):
        if i >= 3: break
        print(f"  - {cond_id}: {cond_data['name']}")

    print(f"\n📊 Sample rating tables created:")
    for i, (table_id, table_data) in enumerate(converted_data["rating_tables"].items()):
        if i >= 3: break
        print(f"  - {table_id}: {table_data.get('title', table_id)}")

if __name__ == "__main__":
    input_file = Path("/home/gslys/gwsGPT/app_simplified/data/rules/master2019ToD_old.json")
    output_file = Path("/home/gslys/gwsGPT/app_simplified/data/rules/master2019ToD.json")

    if not input_file.exists():
        print(f"❌ Error: Input file not found: {input_file}")
        sys.exit(1)

    try:
        convert_json_structure(input_file, output_file)
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
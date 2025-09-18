#!/usr/bin/env python3
"""
Audit script to verify data integrity between original and converted JSON files.
Ensures no adjudication data was lost or modified during conversion.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Set
from deepdiff import DeepDiff

def load_json(file_path: Path) -> Dict[str, Any]:
    """Load JSON file safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {file_path}: {e}")
        sys.exit(1)

def audit_chapters_preservation(original: Dict, converted: Dict) -> bool:
    """Verify all original chapter data is preserved"""
    print("\n🔍 Auditing Chapter Data Preservation...")

    original_chapters = original.get("chapters", {})
    converted_chapters = converted.get("chapters", {})

    if not converted_chapters:
        print("❌ ERROR: No chapters found in converted file!")
        return False

    # Check chapter count
    if len(original_chapters) != len(converted_chapters):
        print(f"❌ ERROR: Chapter count mismatch!")
        print(f"   Original: {len(original_chapters)} chapters")
        print(f"   Converted: {len(converted_chapters)} chapters")
        return False

    # Deep compare each chapter
    chapters_match = True
    for chapter_id, orig_chapter in original_chapters.items():
        if chapter_id not in converted_chapters:
            print(f"❌ ERROR: Missing chapter {chapter_id} in converted file")
            chapters_match = False
            continue

        conv_chapter = converted_chapters[chapter_id]

        # Deep diff comparison
        diff = DeepDiff(orig_chapter, conv_chapter, ignore_order=True)
        if diff:
            print(f"❌ ERROR: Chapter {chapter_id} data differs!")
            print(f"   Differences: {diff}")
            chapters_match = False
        else:
            print(f"✅ Chapter {chapter_id}: {orig_chapter.get('title', 'No title')} - Data intact")

    return chapters_match

def audit_metadata_preservation(original: Dict, converted: Dict) -> bool:
    """Verify metadata is preserved"""
    print("\n🔍 Auditing Metadata Preservation...")

    metadata_keys = ["schema_version", "source", "metadata", "validation", "global", "overall_directions"]
    all_preserved = True

    for key in metadata_keys:
        if key in original:
            if key not in converted:
                print(f"❌ ERROR: Missing metadata key: {key}")
                all_preserved = False
            else:
                diff = DeepDiff(original[key], converted[key], ignore_order=True)
                if diff:
                    print(f"❌ ERROR: Metadata {key} differs!")
                    print(f"   Differences: {diff}")
                    all_preserved = False
                else:
                    print(f"✅ Metadata {key} preserved")

    return all_preserved

def audit_table_data_integrity(original: Dict, converted: Dict) -> bool:
    """Verify all table data is accessible in rating_tables"""
    print("\n🔍 Auditing Table Data Integrity...")

    original_chapters = original.get("chapters", {})
    converted_rating_tables = converted.get("rating_tables", {})

    if not converted_rating_tables:
        print("❌ ERROR: No rating_tables found in converted file!")
        return False

    all_tables_found = True
    table_count = 0

    for chapter_id, chapter_data in original_chapters.items():
        tables = chapter_data.get("tables", {})
        for table_id, table_data in tables.items():
            table_count += 1
            full_table_id = f"{chapter_id}.{table_id}"

            # Check if table exists in rating_tables
            if full_table_id not in converted_rating_tables:
                print(f"❌ ERROR: Table {full_table_id} not found in rating_tables")
                all_tables_found = False
                continue

            # Verify table data integrity
            converted_table = converted_rating_tables[full_table_id]
            original_table_data = table_data

            # The converted table should contain all original data
            # Check if original data is preserved in the 'data' field or directly
            preserved_data = converted_table.get("data", converted_table)

            # Compare core table data
            diff = DeepDiff(original_table_data, preserved_data, ignore_order=True, exclude_paths=["root.id", "root.chapter", "root.chapter_title", "root.table_id", "root.title"])

            if diff:
                print(f"❌ ERROR: Table {full_table_id} data integrity compromised!")
                print(f"   Differences: {diff}")
                all_tables_found = False
            else:
                print(f"✅ Table {full_table_id} data integrity verified")

    print(f"\n📊 Total tables audited: {table_count}")
    return all_tables_found

def audit_condition_creation(converted: Dict) -> bool:
    """Verify conditions were created appropriately"""
    print("\n🔍 Auditing Condition Creation...")

    conditions = converted.get("conditions", {})

    if not conditions:
        print("❌ ERROR: No conditions found in converted file!")
        return False

    print(f"✅ Created {len(conditions)} conditions from chapter data")

    # Check for spine/back conditions specifically
    spine_conditions = []
    for cond_id, cond_data in conditions.items():
        keywords = cond_data.get("keywords", [])
        if any(keyword in ["spine", "back", "musculoskeletal"] for keyword in keywords):
            spine_conditions.append((cond_id, cond_data["name"]))

    if spine_conditions:
        print(f"✅ Found {len(spine_conditions)} spine/back related conditions:")
        for cond_id, name in spine_conditions:
            print(f"   - {cond_id}: {name}")
    else:
        print("⚠️  WARNING: No spine/back conditions identified (may still exist)")

    return True

def run_comprehensive_audit(original_file: Path, converted_file: Path) -> bool:
    """Run comprehensive audit of conversion"""
    print("🔍 VAC ToD JSON Conversion Audit")
    print("=" * 50)

    print(f"Original file: {original_file}")
    print(f"Converted file: {converted_file}")

    # Load files
    original = load_json(original_file)
    converted = load_json(converted_file)

    print(f"\n📊 File Statistics:")
    print(f"Original file size: {original_file.stat().st_size:,} bytes")
    print(f"Converted file size: {converted_file.stat().st_size:,} bytes")

    # Run audits
    audits_passed = []

    audits_passed.append(audit_metadata_preservation(original, converted))
    audits_passed.append(audit_chapters_preservation(original, converted))
    audits_passed.append(audit_table_data_integrity(original, converted))
    audits_passed.append(audit_condition_creation(converted))

    # Summary
    print("\n" + "=" * 50)
    print("🎯 AUDIT SUMMARY")
    print("=" * 50)

    passed_count = sum(audits_passed)
    total_count = len(audits_passed)

    if all(audits_passed):
        print("✅ ALL AUDITS PASSED!")
        print("✅ Data integrity verified - no adjudication data lost")
        print("✅ Conversion successful and safe to use")
        return True
    else:
        print(f"❌ {total_count - passed_count} audit(s) failed")
        print("❌ Please review errors above before using converted file")
        return False

if __name__ == "__main__":
    # Install deepdiff if not available
    try:
        import deepdiff
    except ImportError:
        print("Installing required deepdiff package...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "deepdiff"])
        import deepdiff

    original_file = Path("/home/gslys/gwsGPT/app_simplified/data/rules/master2019ToD_old.json")
    converted_file = Path("/home/gslys/gwsGPT/app_simplified/data/rules/master2019ToD.json")

    if not original_file.exists():
        print(f"❌ Error: Original file not found: {original_file}")
        sys.exit(1)

    if not converted_file.exists():
        print(f"❌ Error: Converted file not found: {converted_file}")
        sys.exit(1)

    success = run_comprehensive_audit(original_file, converted_file)
    sys.exit(0 if success else 1)
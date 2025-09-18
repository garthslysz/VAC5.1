"""
System prompts and prompt management
"""

from pathlib import Path
from typing import Dict, Any
import logging

def load_system_prompt() -> str:
    """Load the main system prompt"""
    try:
        prompt_path = Path("prompts/system_prompt.md")
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logging.error(f"Failed to load system prompt: {e}")
        return DEFAULT_SYSTEM_PROMPT

def load_assessment_flow() -> str:
    """Load the assessment flow instructions"""
    try:
        flow_path = Path("prompts/flows/assessment.md")
        with open(flow_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logging.error(f"Failed to load assessment flow: {e}")
        return ""

def load_adjudicator_tone() -> str:
    """Load the adjudicator tone guidelines"""
    try:
        tone_path = Path("prompts/styles/adjudicator_tone.md")
        with open(tone_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logging.error(f"Failed to load tone guidelines: {e}")
        return ""

def build_complete_system_prompt() -> str:
    """Build the complete system prompt with all components"""
    components = [
        load_system_prompt(),
        "\n\n## Assessment Process\n",
        load_assessment_flow(),
        "\n\n## Communication Style\n",
        load_adjudicator_tone(),
        "\n\n## Available Functions\n",
        FUNCTION_DEFINITIONS
    ]
    
    return "\n".join(filter(None, components))

# Function definitions for the LLM
FUNCTION_DEFINITIONS = """
You have access to these functions to help with assessments:

1. **search_documents(query, jurisdiction, chapter)** - Search indexed regulatory documents
   - Use this to find supporting evidence from official documents
   - Always search before rating to gather table citations

2. **rate_vac_canada(condition, medical_evidence, qol_statement)** - Calculate VAC Canada ratings
   - Uses your master2019ToD.json for deterministic calculations
   - Returns table-by-table MI, bracketing/PCT, QoL, final arithmetic

3. **rate_aus_garp(condition, medical_evidence)** - Calculate Australia GARP V5 ratings
   - Applies impairment tables and lifestyle adjustments
   - Returns GARP points with key drivers

4. **rate_uk_afcs(condition, medical_evidence)** - Calculate UK AFCS/WPS ratings  
   - Maps to tariffs (AFCS) or percentage disablement (WPS)
   - Applies multiple injury rules and GIP where applicable

5. **rate_us_38cfr(condition, medical_evidence)** - Calculate US 38 CFR ratings
   - Uses diagnostic codes and combined ratings table
   - Avoids pyramiding per regulations

## Function Calling Rules

- **Always search first** to gather evidence and table citations
- **Use structured evidence** when calling rating functions
- **Show your reasoning** - search → evidence → rating calculation
- **Quote exact table text** from search results in your ratings
- **Handle missing evidence** by noting "Not documented" and rating conservatively
"""

# Fallback system prompt if file loading fails
DEFAULT_SYSTEM_PROMPT = """
You are the VAC Disability Rating Helper, a specialized assistant that produces transparent, 
table-driven Disability Assessments using Canada ToD (2019), Australia GARP V5, UK (AFCS/WPS), 
and US (38 CFR).

You work exclusively from uploaded evidence and produce standardized, auditable assessments.
Always use the available functions to search documents and calculate ratings.
"""
"""
Score Extraction Utility
Extracts score and justification from analysis markdown
"""

import re
from typing import Tuple, Optional


def extract_score_from_analysis(analysis_text: str) -> Tuple[Optional[int], Optional[str]]:
    """
    Extract score and justification from analysis markdown
    
    Args:
        analysis_text: Full analysis markdown text
        
    Returns:
        Tuple of (score, justification)
    """
    # Pattern to match: **Score: [X]/5** or **Score: X/5** or **Score: +X/5**
    score_pattern = r'\*\*Score:\s*\[?([+-]?\d+)\]?/5\*\*'
    
    score_match = re.search(score_pattern, analysis_text)
    
    if not score_match:
        return None, None
    
    score = int(score_match.group(1))
    
    # Validate score range
    if score < -5 or score > 5:
        return None, None
    
    # Extract justification
    # Look for text after "**Justification:**" until the next "---" or "##"
    justification_pattern = r'\*\*Justification:\*\*\s*\n(.*?)(?:\n---|\n##|$)'
    
    justification_match = re.search(justification_pattern, analysis_text, re.DOTALL)
    
    if justification_match:
        justification = justification_match.group(1).strip()
    else:
        # Fallback: get text after the score section
        score_section_start = score_match.end()
        next_section = re.search(r'\n---|\n##', analysis_text[score_section_start:])
        
        if next_section:
            justification_text = analysis_text[score_section_start:score_section_start + next_section.start()]
        else:
            justification_text = analysis_text[score_section_start:score_section_start + 500]
        
        # Clean up
        justification = justification_text.strip()
        
        # Remove "Justification:" prefix if present
        justification = re.sub(r'^\*\*Justification:\*\*\s*', '', justification)
    
    return score, justification


def validate_score(score: int) -> bool:
    """
    Validate that score is in valid range
    
    Args:
        score: Score value
        
    Returns:
        True if valid, False otherwise
    """
    return -5 <= score <= 5


def get_score_label(score: int) -> str:
    """
    Get human-readable label for score
    
    Args:
        score: Score value (-5 to +5)
        
    Returns:
        Label string
    """
    if score >= 4:
        return "Very Bullish"
    elif score >= 2:
        return "Bullish"
    elif score >= 1:
        return "Slightly Bullish"
    elif score == 0:
        return "Neutral"
    elif score >= -1:
        return "Slightly Bearish"
    elif score >= -3:
        return "Bearish"
    else:
        return "Very Bearish"


def get_expected_movement_range(score: int) -> str:
    """
    Get expected price movement range based on score
    
    Args:
        score: Score value (-5 to +5)
        
    Returns:
        Movement range string
    """
    ranges = {
        5: ">+10%",
        4: "+7% to +10%",
        3: "+4% to +7%",
        2: "+2% to +4%",
        1: "0% to +2%",
        0: "-1% to +1%",
        -1: "0% to -2%",
        -2: "-2% to -4%",
        -3: "-4% to -7%",
        -4: "-7% to -10%",
        -5: "<-10%"
    }
    
    return ranges.get(score, "Unknown")

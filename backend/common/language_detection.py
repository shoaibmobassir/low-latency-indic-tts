"""
Language Detection for TTS
Automatically detects language from text to prevent mismatches.
"""

import logging
import re
from typing import Literal, Optional

logger = logging.getLogger(__name__)

# Unicode ranges for Indic scripts
GUJARATI_RANGE = (0x0A80, 0x0AFF)
MARATHI_RANGE = (0x0900, 0x097F)  # Devanagari (shared with Hindi, but we can detect context)

# Common words/phrases for each language
GUJARATI_MARKERS = [
    'આ', 'એ', 'અને', 'તે', 'આવે', 'જાય', 'છે', 'હતું', 'હશે',
    'કરે', 'કર્યું', 'થાય', 'થયું', 'છે', 'છતું', 'છતી'
]

MARATHI_MARKERS = [
    'आहे', 'आणि', 'ते', 'या', 'होते', 'होतात', 'करते', 'करतात',
    'येते', 'येतात', 'जाते', 'जातात', 'झाले', 'झालेल्या', 'कळविण्यात'
]


def detect_language(text: str) -> Optional[Literal["gu", "mr"]]:
    """
    Detect language from text using script analysis and word markers.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Detected language code ('gu' or 'mr') or None if uncertain
    """
    if not text or not text.strip():
        return None
    
    # Count characters in each script range
    gujarati_chars = 0
    marathi_chars = 0
    
    for char in text:
        code_point = ord(char)
        if GUJARATI_RANGE[0] <= code_point <= GUJARATI_RANGE[1]:
            gujarati_chars += 1
        elif MARATHI_RANGE[0] <= code_point <= MARATHI_RANGE[1]:
            marathi_chars += 1
    
    # Count word markers
    text_lower = text.lower()
    gujarati_markers_found = sum(1 for marker in GUJARATI_MARKERS if marker in text_lower)
    marathi_markers_found = sum(1 for marker in MARATHI_MARKERS if marker in text_lower)
    
    # Decision logic
    if gujarati_chars > 0 and marathi_chars == 0:
        logger.debug(f"[LangDetect] Detected Gujarati: {gujarati_chars} Gujarati chars")
        return "gu"
    elif marathi_chars > 0 and gujarati_chars == 0:
        logger.debug(f"[LangDetect] Detected Marathi: {marathi_chars} Marathi chars")
        return "mr"
    elif gujarati_chars > marathi_chars * 2:
        logger.debug(f"[LangDetect] Detected Gujarati: {gujarati_chars} vs {marathi_chars} chars")
        return "gu"
    elif marathi_chars > gujarati_chars * 2:
        logger.debug(f"[LangDetect] Detected Marathi: {marathi_chars} vs {gujarati_chars} chars")
        return "mr"
    elif marathi_markers_found > gujarati_markers_found:
        logger.debug(f"[LangDetect] Detected Marathi: {marathi_markers_found} markers")
        return "mr"
    elif gujarati_markers_found > marathi_markers_found:
        logger.debug(f"[LangDetect] Detected Gujarati: {gujarati_markers_found} markers")
        return "gu"
    else:
        logger.warning(f"[LangDetect] Uncertain: gu_chars={gujarati_chars}, mr_chars={marathi_chars}")
        return None


def validate_language_match(text: str, selected_language: Literal["gu", "mr"]) -> tuple[bool, Optional[Literal["gu", "mr"]]]:
    """
    Validate if selected language matches the text, and suggest correct language if not.
    
    Args:
        text: Input text
        selected_language: User-selected language
        
    Returns:
        Tuple of (is_match, detected_language)
    """
    detected = detect_language(text)
    
    if detected is None:
        # Can't detect, assume user selection is correct
        return True, selected_language
    
    if detected == selected_language:
        return True, selected_language
    
    # Mismatch detected
    logger.warning(
        f"[LangDetect] Language mismatch: selected={selected_language}, "
        f"detected={detected}, text_preview={text[:50]}"
    )
    return False, detected



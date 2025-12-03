"""
Smart Chunking Algorithms for Streaming TTS
Implements breath group heuristic and lookahead rolling window for <100ms latency.
"""

import re
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

# Priority order for splitting (higher priority = split first)
SPLIT_PRIORITY = {
    '.': 6,
    '?': 5,
    '!': 4,
    ';': 3,
    ',': 2,
    ' and ': 1,
    ' but ': 1,
    ' or ': 1,
    ' તો ': 1,  # Gujarati: "then"
    ' અને ': 1,  # Gujarati: "and"
    ' પણ ': 1,  # Gujarati: "but"
    ' आणि ': 1,  # Marathi: "and"
    ' पण ': 1,  # Marathi: "but"
    ' म्हणून ': 1,  # Marathi: "so"
}

# Word count threshold for soft breaks
SOFT_BREAK_THRESHOLD = 5  # Split on soft boundaries if chunk exceeds this many words


class SmartChunker:
    """
    Intelligent text chunker using breath group heuristic.
    
    Splits text on soft boundaries (commas, conjunctions) when chunks get too long,
    ensuring <100ms latency by not waiting for sentence endings.
    """
    
    def __init__(self, max_words: int = 10, min_words: int = 2):
        """
        Initialize smart chunker.
        
        Args:
            max_words: Maximum words per chunk (triggers soft break search)
            min_words: Minimum words per chunk (prevents tiny chunks)
        """
        self.max_words = max_words
        self.min_words = min_words
    
    def split_text(self, text: str) -> List[str]:
        """
        Split text into chunks using breath group heuristic.
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        chunks = []
        remaining = text
        processed_length = 0
        
        while remaining and remaining.strip():
            chunk = self._extract_next_chunk(remaining)
            if chunk and chunk.strip():
                chunks.append(chunk.strip())
                # Find the chunk in remaining text (handle whitespace variations)
                chunk_start = remaining.find(chunk.strip())
                if chunk_start != -1:
                    # Remove processed chunk from remaining text
                    chunk_end = chunk_start + len(chunk.strip())
                    remaining = remaining[chunk_end:].strip()
                    processed_length += len(chunk.strip())
                else:
                    # Chunk not found exactly, try to remove by length
                    remaining = remaining[len(chunk):].strip()
                    processed_length += len(chunk)
            else:
                # No valid chunk found, take remaining as-is (CRITICAL: don't lose last part)
                if remaining and remaining.strip():
                    chunks.append(remaining.strip())
                    processed_length += len(remaining.strip())
                break
        
        # CRITICAL: Ensure last part is always included
        # Check if we have remaining text that wasn't processed
        if remaining and remaining.strip():
            remaining_clean = remaining.strip()
            # Check if this remaining text is already in chunks
            all_chunks_text = ' '.join(chunks)
            if remaining_clean not in all_chunks_text:
                logger.warning(f"[Chunker] Adding remaining text as final chunk: '{remaining_clean[:50]}...'")
                chunks.append(remaining_clean)
        
        # CRITICAL: Verify no text was lost by comparing character counts
        reconstructed = ' '.join(chunks)
        # Normalize both for comparison (remove extra spaces)
        original_normalized = re.sub(r'\s+', ' ', text.strip())
        reconstructed_normalized = re.sub(r'\s+', ' ', reconstructed.strip())
        
        # Compare character by character (ignoring whitespace differences)
        original_chars = len(original_normalized.replace(' ', ''))
        reconstructed_chars = len(reconstructed_normalized.replace(' ', ''))
        
        if reconstructed_chars < original_chars:
            logger.error(
                f"[Chunker] ⚠️ Text loss detected: original={original_chars} chars, "
                f"reconstructed={reconstructed_chars} chars, loss={original_chars - reconstructed_chars} chars"
            )
            # Find missing text by comparing positions
            missing_text = original_normalized[len(reconstructed_normalized):].strip()
            if missing_text:
                logger.warning(f"[Chunker] Adding missing text as final chunk: '{missing_text[:50]}...'")
                chunks.append(missing_text)
        
        # Final verification: ensure we have all text
        final_reconstructed = ' '.join(chunks)
        final_normalized = re.sub(r'\s+', ' ', final_reconstructed.strip())
        final_chars = len(final_normalized.replace(' ', ''))
        
        if final_chars < original_chars:
            logger.error(
                f"[Chunker] ❌ CRITICAL: Still missing text after recovery: "
                f"original={original_chars}, final={final_chars}, loss={original_chars - final_chars}"
            )
            # Last resort: add everything that's missing
            if len(final_normalized) < len(original_normalized):
                remaining_all = original_normalized[len(final_normalized):].strip()
                if remaining_all:
                    logger.warning(f"[Chunker] Last resort: adding all remaining text: '{remaining_all[:50]}...'")
                    chunks.append(remaining_all)
        
        logger.info(f"[Chunker] Split into {len(chunks)} chunks: {[len(c) for c in chunks]} chars each")
        return chunks
    
    def _extract_next_chunk(self, text: str) -> Optional[str]:
        """
        Extract next chunk from text using priority-based splitting.
        
        Args:
            text: Remaining text to process
            
        Returns:
            Next chunk (including split character) or None
        """
        if not text:
            return None
        
        # Count words in potential chunk
        words = text.split()
        word_count = len(words)
        
        # If text is short enough, return as-is
        if word_count <= self.max_words:
            # Check for hard boundaries first
            for boundary in ['.', '?', '!']:
                if boundary in text:
                    idx = text.find(boundary)
                    chunk = text[:idx + 1]
                    if self._is_valid_chunk(chunk):
                        return chunk
            # No hard boundary, return entire text
            return text
        
        # Text is too long, look for soft breaks
        # Sort boundaries by priority (highest first)
        boundaries = sorted(SPLIT_PRIORITY.items(), key=lambda x: x[1], reverse=True)
        
        for boundary, priority in boundaries:
            # Search for boundary in text
            idx = text.find(boundary)
            if idx != -1:
                # Check if chunk before boundary is valid
                chunk = text[:idx + len(boundary)]
                if self._is_valid_chunk(chunk):
                    return chunk
        
        # No suitable boundary found, take first max_words
        # BUT: ensure we don't take more than available
        chunk_words = words[:min(self.max_words, word_count)]
        chunk = ' '.join(chunk_words)
        
        # Ensure we return something even if it's the whole text
        if not chunk and text:
            return text
        
        return chunk
    
    def _is_valid_chunk(self, chunk: str) -> bool:
        """
        Check if chunk is valid (meets minimum word requirement).
        
        Args:
            chunk: Text chunk to validate
            
        Returns:
            True if chunk is valid
        """
        words = chunk.split()
        return len(words) >= self.min_words


class LookaheadBuffer:
    """
    Lookahead rolling window for maintaining prosody context.
    
    Uses previous chunk tokens as context for current chunk generation,
    ensuring smooth prosody flow across chunk boundaries.
    """
    
    def __init__(self, context_size: int = 3):
        """
        Initialize lookahead buffer.
        
        Args:
            context_size: Number of words to use as context
        """
        self.context_size = context_size
        self.previous_tokens: List[str] = []
    
    def get_context_window(self, current_chunk: str) -> Tuple[str, str]:
        """
        Get context window for current chunk.
        
        Args:
            current_chunk: Current chunk text
            
        Returns:
            Tuple of (context_text, current_text)
            context_text includes previous tokens for prosody
            current_text is the actual chunk to synthesize
        """
        current_words = current_chunk.split()
        
        # Build context from previous tokens
        context_words = self.previous_tokens[-self.context_size:] if self.previous_tokens else []
        context_text = ' '.join(context_words + current_words[:self.context_size])
        
        # Update previous tokens
        self.previous_tokens = current_words
        
        return context_text, current_chunk
    
    def reset(self):
        """Reset buffer state."""
        self.previous_tokens = []


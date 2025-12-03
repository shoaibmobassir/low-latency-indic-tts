"""
Packet-based Streaming TTS
Generates and sends audio packets immediately as text chunks are processed.
Ensures constant latency regardless of text size.
"""

import logging
import time
from typing import Generator, Tuple
import numpy as np

from backend.common.smart_chunking import SmartChunker
from backend.common.config import DEFAULT_SAMPLE_RATE, FIRST_CHUNK_SIZE_MS, SUBSEQUENT_CHUNK_SIZE_MS
from backend.common.streaming import wav_to_chunks, normalize_audio

logger = logging.getLogger(__name__)


class PacketStreamingGenerator:
    """
    Generates TTS audio in packets with constant latency.
    
    Key features:
    - Text is chunked into small packets (5-10 words)
    - Each packet is processed independently
    - Audio packets are yielded immediately as they're generated
    - First packet latency is constant regardless of total text size
    """
    
    def __init__(
        self,
        inference_func,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
        words_per_packet: int = 5,
        packet_overlap_words: int = 1
    ):
        """
        Initialize packet streaming generator.
        
        Args:
            inference_func: Function(text, language) -> (waveform, sample_rate)
            sample_rate: Target sample rate
            words_per_packet: Number of words per text packet (smaller = faster first packet)
            packet_overlap_words: Words to overlap between packets for smooth transitions
        """
        self.inference_func = inference_func
        self.sample_rate = sample_rate
        self.chunker = SmartChunker(max_words=words_per_packet)
        self.packet_overlap_words = packet_overlap_words
        
        logger.info(
            f"[PacketStream] Initialized: words_per_packet={words_per_packet}, "
            f"overlap={packet_overlap_words}, sample_rate={sample_rate}"
        )
    
    def generate_packets(
        self,
        text: str,
        language: str
    ) -> Generator[Tuple[np.ndarray, int], None, None]:
        """
        Generate audio packets from text with constant first-packet latency.
        
        Args:
            text: Full text to synthesize
            language: Language code
            
        Yields:
            Tuples of (waveform, sample_rate) for each packet
        """
        if not text or not text.strip():
            return
        
        # Split text into packets (small chunks for fast processing)
        text_packets = self.chunker.split_text(text)
        
        if not text_packets:
            logger.warning("[PacketStream] No packets generated from text")
            return
        
        logger.info(f"[PacketStream] Split text into {len(text_packets)} packets: {[len(p) for p in text_packets]} chars each")
        
        # Verify all packets are non-empty
        text_packets = [p for p in text_packets if p and p.strip()]
        if len(text_packets) == 0:
            logger.error("[PacketStream] No valid packets after filtering")
            return
        
        logger.info(
            f"[PacketStream] Processing {len(text_packets)} valid packets. "
            f"Last packet preview: '{text_packets[-1][:50]}...'"
        )
        
        # Process each packet independently and yield immediately
        packets_yielded = 0
        for i, packet_text in enumerate(text_packets):
            if not packet_text or not packet_text.strip():
                logger.warning(f"[PacketStream] Empty packet {i+1}, skipping")
                continue
                
            packet_start = time.time()
            is_last_packet = (i == len(text_packets) - 1)
            
            try:
                # Generate audio for this packet only
                # Note: inference_func should handle language detection internally
                waveform, sr = self.inference_func(packet_text.strip(), language)
                
                if waveform is None or len(waveform) == 0:
                    logger.warning(f"[PacketStream] Empty waveform for packet {i+1}, skipping")
                    if is_last_packet:
                        logger.error(f"[PacketStream] ❌ CRITICAL: Last packet ({i+1}) produced empty waveform!")
                    continue
                
                # Normalize audio
                waveform = normalize_audio(waveform)
                
                # Ensure correct sample rate
                if sr != self.sample_rate:
                    # Simple resampling (for production, use proper resampling)
                    ratio = self.sample_rate / sr
                    new_length = int(len(waveform) * ratio)
                    waveform = np.interp(
                        np.linspace(0, len(waveform), new_length),
                        np.arange(len(waveform)),
                        waveform
                    )
                
                packet_time = (time.time() - packet_start) * 1000
                logger.info(
                    f"[PacketStream] Packet {i+1}/{len(text_packets)} {'(LAST)' if is_last_packet else ''}: "
                    f"'{packet_text[:30]}...' -> {len(waveform)} samples, {packet_time:.1f}ms"
                )
                
                # Yield immediately - don't wait for other packets
                yield waveform, self.sample_rate
                packets_yielded += 1
                
                if is_last_packet:
                    logger.info(f"[PacketStream] ✅ Last packet ({i+1}) successfully yielded: {len(waveform)} samples")
                
            except Exception as e:
                logger.error(f"[PacketStream] Error processing packet {i+1} ('{packet_text[:30]}...'): {e}")
                if is_last_packet:
                    logger.error(f"[PacketStream] ❌ CRITICAL: Last packet ({i+1}) failed with error: {e}")
                # Continue with next packet on error
                continue
        
        logger.info(
            f"[PacketStream] ✅ Completed processing: {packets_yielded}/{len(text_packets)} packets yielded "
            f"(expected {len(text_packets)} packets)"
        )
        
        if packets_yielded < len(text_packets):
            logger.error(
                f"[PacketStream] ⚠️ WARNING: Only {packets_yielded}/{len(text_packets)} packets were yielded! "
                f"Missing {len(text_packets) - packets_yielded} packet(s)"
            )


def stream_audio_packets(
    text: str,
    language: str,
    inference_func,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    words_per_packet: int = 5
) -> Generator[bytes, None, None]:
    """
    Stream audio packets as WAV bytes with constant latency.
    
    Args:
        text: Text to synthesize
        language: Language code
        inference_func: Function to generate audio from text
        sample_rate: Target sample rate
        words_per_packet: Words per packet (smaller = faster first packet)
        
    Yields:
        WAV-encoded audio chunks as bytes
    """
    generator = PacketStreamingGenerator(
        inference_func=inference_func,
        sample_rate=sample_rate,
        words_per_packet=words_per_packet
    )
    
    first_packet_sent = False
    packet_count = 0
    total_chunks_yielded = 0
    
    # Get total packet count for last packet detection
    from backend.common.smart_chunking import SmartChunker
    chunker = SmartChunker(max_words=words_per_packet)
    text_packets = chunker.split_text(text)
    text_packets = [p for p in text_packets if p and p.strip()]
    total_packets = len(text_packets)
    
    logger.info(f"[PacketStream] Will process {total_packets} packets total")
    
    try:
        for waveform, sr in generator.generate_packets(text, language):
            if waveform is None or len(waveform) == 0:
                logger.warning(f"[PacketStream] Skipping empty waveform")
                continue
                
            packet_count += 1
            is_last_packet = (packet_count == total_packets)
            
            # Convert waveform to int16 for chunking
            if waveform.dtype != np.int16:
                waveform_int16 = (waveform * 32767).astype(np.int16)
            else:
                waveform_int16 = waveform
            
            # For first packet: send smaller chunks for faster perceived latency
            if not first_packet_sent:
                # Send first packet in small chunks (10ms)
                chunks = list(wav_to_chunks(waveform_int16, sr, FIRST_CHUNK_SIZE_MS))
                chunks_yielded_this_packet = 0
                for chunk_bytes in chunks:
                    yield chunk_bytes
                    chunks_yielded_this_packet += 1
                    total_chunks_yielded += 1
                first_packet_sent = True
                logger.info(f"[PacketStream] First packet sent: {chunks_yielded_this_packet} chunks")
            else:
                # Subsequent packets: send in larger chunks (30ms) for efficiency
                chunks = list(wav_to_chunks(waveform_int16, sr, SUBSEQUENT_CHUNK_SIZE_MS))
                chunks_yielded_this_packet = 0
                is_last_packet = (packet_count == total_packets)
                
                for chunk_bytes in chunks:
                    yield chunk_bytes
                    chunks_yielded_this_packet += 1
                    total_chunks_yielded += 1
                
                # CRITICAL: Log last packet chunks to verify all are sent
                if is_last_packet:
                    logger.info(
                        f"[PacketStream] ✅ Last packet ({packet_count}/{total_packets}) sent: "
                        f"{chunks_yielded_this_packet} chunks, {len(waveform_int16)} samples"
                    )
                else:
                    logger.debug(f"[PacketStream] Packet {packet_count}/{total_packets} sent: {chunks_yielded_this_packet} chunks")
        
        # After loop completes, verify we processed all packets
        logger.info(
            f"[PacketStream] Stream complete: {packet_count}/{total_packets} packets processed, "
            f"{total_chunks_yielded} total chunks yielded"
        )
        
        if packet_count < total_packets:
            logger.error(
                f"[PacketStream] ❌ CRITICAL: Only {packet_count}/{total_packets} packets were processed! "
                f"Missing {total_packets - packet_count} packet(s)"
            )
        elif packet_count == total_packets:
            logger.info(f"[PacketStream] ✅ All {total_packets} packets successfully processed and yielded")
        
    except Exception as e:
        logger.error(f"[PacketStream] Error in stream_audio_packets: {e}", exc_info=True)
        raise


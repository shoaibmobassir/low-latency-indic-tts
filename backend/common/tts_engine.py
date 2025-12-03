"""
Unified TTS Engine
GPU-optimized TTS inference engine supporting MMS-TTS and IndicTTS.
"""

import logging
import time
from pathlib import Path
from typing import Generator, Literal, Optional, Tuple

import numpy as np
import soundfile as sf
import torch
from transformers import AutoTokenizer, VitsModel

from backend.common.config import (
    DEFAULT_CHUNK_SIZE_MS,
    DEFAULT_SAMPLE_RATE,
    INDICTTS_FALLBACK,
    MMS_TTS_GU_MODEL,
    MMS_TTS_MR_MODEL,
    MODEL_INDICTTS,
    MODEL_MMS_TTS,
    USE_CASE_FALLBACK,
    USE_CASE_TELECOM,
    USE_CASE_WEB_UI,
    USE_CASE_MODEL_MAP,
    FIRST_CHUNK_SIZE_MS,
    SUBSEQUENT_CHUNK_SIZE_MS,
    LOW_LATENCY_MODE,
    USE_FP16_ON_CUDA,
)
from backend.common.device_utils import get_optimal_device
from backend.common.streaming import (
    normalize_audio,
    to_g711_ulaw,
    to_pcm_16k,
    to_pcm_8k,
    trim_silence,
    wav_to_chunks,
)

logger = logging.getLogger(__name__)

Language = Literal["gu", "mr"]
ModelType = Literal["mms_tts", "indictts"]
UseCase = Literal["web_ui", "telecom", "fallback"]


class TTSEngine:
    """
    Unified TTS Engine for GPU-accelerated inference.
    
    Supports:
    - MMS-TTS (high quality, Web UI)
    - IndicTTS (fallback, gTTS)
    """

    def __init__(self):
        """Initialize TTS Engine with device detection."""
        self.device_type, self.device = get_optimal_device()
        
        # Model instances
        self.mms_tts_models: dict[str, Tuple[VitsModel, AutoTokenizer]] = {}
        self.indictts_loaded = False
        
        # ONNX optimizer for GPU acceleration
        try:
            from backend.common.onnx_optimizer import ONNXOptimizer
            self.onnx_optimizer = ONNXOptimizer()
            if self.device_type == "cuda":
                providers = self.onnx_optimizer.get_providers()
                if "CUDAExecutionProvider" in providers:
                    logger.info("[TTS] ONNX GPU acceleration available")
                else:
                    logger.info("[TTS] ONNX GPU not available, using PyTorch")
            else:
                logger.info("[TTS] ONNX optimizer initialized (CPU mode)")
        except Exception as e:
            logger.warning(f"[TTS] ONNX optimizer initialization failed: {e}")
            self.onnx_optimizer = None
        
        logger.info(f"[TTS] Engine initialized on device: {self.device} ({self.device_type})")
    
    def load_mms_tts(self, language: Language) -> None:
        """
        Load MMS-TTS model for specified language.
        
        Args:
            language: Language code ('gu' or 'mr')
        """
        if language in self.mms_tts_models:
            logger.info(f"[TTS] MMS-TTS model for {language} already loaded")
            return
        
        model_name = MMS_TTS_GU_MODEL if language == "gu" else MMS_TTS_MR_MODEL
        
        try:
            logger.info(f"[TTS] Loading MMS-TTS model: {model_name} for {language}")
            start_time = time.time()
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # Load model
            model = VitsModel.from_pretrained(model_name)
            model.to(self.device)
            model.eval()
            
            # Use FP16 for CUDA if enabled (1.5-2x speedup on H100)
            if self.device_type == "cuda" and USE_FP16_ON_CUDA and torch.cuda.is_available():
                try:
                    model = model.half()
                    logger.info("[TTS] Enabled FP16 mixed precision for CUDA (low-latency mode)")
                except Exception as e:
                    logger.warning(f"[TTS] Could not convert to FP16: {e}. Using FP32.")
            
            load_time = (time.time() - start_time) * 1000
            self.mms_tts_models[language] = (model, tokenizer)
            
            logger.info(
                f"[TTS] Model={MODEL_MMS_TTS} Device={self.device_type} "
                f"Language={language} LoadTime={load_time:.1f}ms"
            )
            
        except Exception as e:
            logger.error(f"[TTS] Failed to load MMS-TTS model for {language}: {e}")
            raise
    
    def load_indictts(self, language: Language) -> None:
        """
        Load IndicTTS (gTTS fallback) for specified language.
        
        Args:
            language: Language code ('gu' or 'mr')
        """
        if self.indictts_loaded:
            logger.info("[TTS] IndicTTS already loaded")
            return
        
        if not INDICTTS_FALLBACK:
            raise ValueError("IndicTTS fallback is disabled in config")
        
        try:
            logger.info(f"[TTS] Loading IndicTTS (gTTS fallback) for {language}")
            # gTTS doesn't require model loading, just mark as loaded
            self.indictts_loaded = True
            
            logger.info(
                f"[TTS] Model={MODEL_INDICTTS} Device=cpu "
                f"Language={language} LoadTime=0ms"
            )
            
        except Exception as e:
            logger.error(f"[TTS] Failed to load IndicTTS: {e}")
            raise
    
    def select_model(self, use_case: UseCase) -> ModelType:
        """
        Select model based on use case.
        
        Args:
            use_case: Use case ('web_ui', 'telecom', 'fallback')
            
        Returns:
            Model type to use
        """
        return USE_CASE_MODEL_MAP.get(use_case, MODEL_MMS_TTS)
    
    def infer_wav(
        self,
        text: str,
        language: Language,
        use_case: UseCase = USE_CASE_WEB_UI,
        model_type: Optional[ModelType] = None
    ) -> Tuple[np.ndarray, int]:
        """
        Generate complete WAV audio from text.
        
        Args:
            text: Text to convert to speech
            language: Language code ('gu' or 'mr')
            use_case: Use case for model selection
            model_type: Override model type (if None, uses use_case)
            
        Returns:
            Tuple of (waveform, sample_rate)
        """
        if model_type is None:
            model_type = self.select_model(use_case)
        
        start_time = time.time()
        
        try:
            if model_type == MODEL_MMS_TTS:
                waveform, sample_rate = self._infer_mms_tts(text, language)
            elif model_type == MODEL_INDICTTS:
                waveform, sample_rate = self._infer_indictts(text, language)
            else:
                raise ValueError(f"Unknown model type: {model_type}")
            
            # Normalize audio
            waveform = normalize_audio(waveform)
            
            # Trim silence
            waveform = trim_silence(waveform, sample_rate)
            
            inference_time = (time.time() - start_time) * 1000
            
            logger.info(
                f"[TTS] Model={model_type} Device={self.device_type} "
                f"Duration={inference_time:.1f}ms Language={language}"
            )
            
            return waveform, sample_rate
            
        except Exception as e:
            logger.error(f"[TTS] Inference failed: {e}")
            raise
    
    def infer_chunked(
        self,
        text: str,
        language: Language,
        use_case: UseCase = USE_CASE_TELECOM,
        chunk_ms: int = DEFAULT_CHUNK_SIZE_MS,
        model_type: Optional[ModelType] = None,
        low_latency: bool = LOW_LATENCY_MODE,
        streaming: bool = True
    ) -> Generator[bytes, None, None]:
        """
        Generate audio in chunks for streaming with constant latency.
        
        Uses packet-based streaming to ensure first packet latency is constant
        regardless of text size. Text is split into small packets, each processed
        independently and sent immediately.
        
        Args:
            text: Text to convert to speech
            language: Language code ('gu' or 'mr')
            use_case: Use case for model selection
            chunk_ms: Chunk size in milliseconds (used for subsequent chunks if low_latency=True)
            model_type: Override model type (if None, uses use_case)
            low_latency: Enable low-latency optimizations (smaller first chunk)
            streaming: Use packet-based streaming (True) or generate full audio first (False)
            
        Yields:
            Binary audio chunks (WAV format) sent immediately as packets are generated
        """
        if model_type is None:
            model_type = self.select_model(use_case)
        
        # Use packet-based streaming for constant latency
        if streaming:
            from backend.common.packet_streaming import stream_audio_packets
            
            # Create inference function for the selected model
            if model_type == MODEL_MMS_TTS:
                inference_func = lambda t, l: self._infer_mms_tts(t, l)
            elif model_type == MODEL_INDICTTS:
                inference_func = lambda t, l: self._infer_indictts(t, l)
            else:
                raise ValueError(f"Unsupported model type for streaming: {model_type}")
            
            # Stream packets with constant latency
            for chunk_bytes in stream_audio_packets(
                text=text,
                language=language,
                inference_func=inference_func,
                sample_rate=DEFAULT_SAMPLE_RATE,
                words_per_packet=5  # Small packets for fast first response
            ):
                yield chunk_bytes
        else:
            # Fallback: Generate full audio and chunk it (for compatibility)
            waveform, sample_rate = self.infer_wav(text, language, use_case, model_type)
            
            # Convert to int16 for chunking
            if waveform.dtype != np.int16:
                waveform_int16 = (waveform * 32767).astype(np.int16)
            else:
                waveform_int16 = waveform
            
            if low_latency:
                first_chunk_size_ms = FIRST_CHUNK_SIZE_MS
                subsequent_chunk_size_ms = SUBSEQUENT_CHUNK_SIZE_MS
                
                chunks = list(wav_to_chunks(waveform_int16, sample_rate, first_chunk_size_ms))
                if chunks:
                    yield chunks[0]
                    remaining_waveform = waveform_int16[int(first_chunk_size_ms * sample_rate / 1000):]
                    if len(remaining_waveform) > 0:
                        for chunk in wav_to_chunks(remaining_waveform, sample_rate, subsequent_chunk_size_ms):
                            yield chunk
            else:
                for chunk in wav_to_chunks(waveform_int16, sample_rate, chunk_ms):
                    yield chunk
    
    def _infer_mms_tts(self, text: str, language: Language) -> Tuple[np.ndarray, int]:
        """Internal: MMS-TTS inference."""
        # Validate input text
        if not text or not text.strip():
            raise ValueError("Input text is empty or contains only whitespace")
        
        # Auto-detect language FIRST - always prioritize detection over user selection
        from backend.common.language_detection import detect_language
        original_language = language  # Keep track of original selection
        detected_lang = detect_language(text)
        
        # ALWAYS use detected language if available and different from selection
        if detected_lang:
            if detected_lang != language:
                logger.warning(
                    f"[TTS] ⚠️ Language auto-correction: user selected '{original_language}', "
                    f"but text is detected as '{detected_lang}'. Using '{detected_lang}'."
                )
                language = detected_lang
            else:
                logger.debug(f"[TTS] ✓ Language confirmed: {language}")
        else:
            logger.info(f"[TTS] Language detection uncertain, using user selection: {language}")
        
        if language not in self.mms_tts_models:
            self.load_mms_tts(language)
        
        model, tokenizer = self.mms_tts_models[language]
        
        # Tokenize - ensure inputs are properly formatted
        try:
            inputs = tokenizer(text, return_tensors="pt")
        except Exception as e:
            logger.error(f"[TTS] Tokenization failed: {e}")
            # Try with detected language if different from current
            if detected_lang and detected_lang != language:
                logger.info(f"[TTS] Retrying with detected language: {detected_lang}")
                if detected_lang not in self.mms_tts_models:
                    self.load_mms_tts(detected_lang)
                model, tokenizer = self.mms_tts_models[detected_lang]
                try:
                    inputs = tokenizer(text, return_tensors="pt")
                except Exception as e2:
                    raise ValueError(
                        f"Failed to tokenize text with both selected ({original_language}) "
                        f"and detected ({detected_lang}) languages. Error: {e2}"
                    )
            else:
                raise ValueError(
                    f"Failed to tokenize text. The text might not be in the correct language ({original_language}).\n"
                    f"Error: {e}\n"
                    f"Tip: Make sure the selected language matches the text language."
                )
        
        # Validate tokenization result
        if "input_ids" not in inputs:
            raise ValueError("Tokenizer did not return input_ids. The text might not be compatible with this model.")
        
        input_ids = inputs["input_ids"]
        
        # Check if input_ids is empty or has invalid shape
        if input_ids.numel() == 0 or input_ids.shape[1] == 0:
            # Try with detected language if available
            if detected_lang and detected_lang != language:
                logger.info(f"[TTS] Empty tokenization, retrying with detected language: {detected_lang}")
                if detected_lang not in self.mms_tts_models:
                    self.load_mms_tts(detected_lang)
                model, tokenizer = self.mms_tts_models[detected_lang]
                inputs = tokenizer(text, return_tensors="pt")
                input_ids = inputs["input_ids"]
                
                if input_ids.numel() == 0 or input_ids.shape[1] == 0:
                    raise ValueError(
                        f"Tokenization produced empty input even with detected language ({detected_lang}).\n"
                        f"This usually means:\n"
                        f"1. The text contains only unsupported characters\n"
                        f"2. The tokenizer cannot process this text\n"
                        f"Text provided: {text[:100]}..."
                    )
                # Update language for rest of function
                language = detected_lang
                logger.info(f"[TTS] Successfully tokenized with detected language: {detected_lang}")
            else:
                # Try one more time with direct detection
                if detected_lang and detected_lang != language:
                    logger.info(f"[TTS] Final retry with detected language: {detected_lang}")
                    if detected_lang not in self.mms_tts_models:
                        self.load_mms_tts(detected_lang)
                    model, tokenizer = self.mms_tts_models[detected_lang]
                    inputs = tokenizer(text, return_tensors="pt")
                    input_ids = inputs["input_ids"]
                    if input_ids.numel() > 0 and input_ids.shape[1] > 0:
                        language = detected_lang
                        logger.info(f"[TTS] Successfully tokenized with detected language: {detected_lang}")
                    else:
                        raise ValueError(
                            f"Tokenization failed with both selected ({original_language}) and detected ({detected_lang}) languages.\n"
                            f"This usually means:\n"
                            f"1. The text contains only unsupported characters\n"
                            f"2. The tokenizer cannot process this text\n"
                            f"Text provided: {text[:100]}..."
                        )
                else:
                    raise ValueError(
                        f"Tokenization produced empty input with language {language}.\n"
                        f"Original selection: {original_language}, Detected: {detected_lang}\n"
                        f"This usually means:\n"
                        f"1. The text language doesn't match the model language\n"
                        f"2. The text contains only unsupported characters\n"
                        f"3. The tokenizer cannot process this text\n"
                        f"Text provided: {text[:100]}...\n"
                        f"Tip: The system detected this might be {detected_lang if detected_lang else 'unknown'} language."
                    )
        
        # Ensure input_ids are Long/Int tensors (not float)
        inputs["input_ids"] = input_ids.long()
        
        # MPS has a limitation: output channels > 65536 not supported
        # For long texts, use CPU to avoid this limitation
        # Also, MPS doesn't provide significant speedup for MMS-TTS
        use_device = "cpu" if self.device_type == "mps" else self.device
        
        if use_device == "cpu":
            # Keep inputs on CPU, ensure proper types
            # input_ids must be Long, other tensors can be float
            processed_inputs = {}
            for k, v in inputs.items():
                if k == "input_ids":
                    processed_inputs[k] = v.cpu().long()
                else:
                    processed_inputs[k] = v.cpu()
            inputs = processed_inputs
            model_cpu = model.cpu()
        else:
            # Move to device, ensure input_ids are Long
            processed_inputs = {}
            for k, v in inputs.items():
                if k == "input_ids":
                    processed_inputs[k] = v.to(self.device).long()
                else:
                    processed_inputs[k] = v.to(self.device)
            inputs = processed_inputs
            model_cpu = model
        
        # Generate with FP16 if enabled
        with torch.no_grad():
            if self.device_type == "cuda" and USE_FP16_ON_CUDA and model_cpu.dtype == torch.float16:
                # Ensure inputs are FP16 compatible (input_ids stay int, others can be FP16)
                fp16_inputs = {}
                for k, v in inputs.items():
                    if k == "input_ids":
                        fp16_inputs[k] = v  # Keep as int
                    elif v.dtype == torch.float32:
                        fp16_inputs[k] = v.half()  # Convert to FP16
                    else:
                        fp16_inputs[k] = v
                output = model_cpu(**fp16_inputs).waveform
            else:
                output = model_cpu(**inputs).waveform
        
        # Move to CPU and convert to numpy
        # Convert FP16 to FP32 for numpy compatibility
        if output.dtype == torch.float16:
            waveform = output.cpu().float().squeeze().numpy()
        else:
            waveform = output.cpu().squeeze().numpy()
        sample_rate = 16000  # MMS-TTS default
        
        # Move model back to original device if needed
        if use_device == "cpu" and self.device_type != "cpu":
            model.to(self.device)
        
        return waveform, sample_rate
    
    def _infer_indictts(self, text: str, language: Language) -> Tuple[np.ndarray, int]:
        """Internal: IndicTTS (gTTS) inference."""
        if not self.indictts_loaded:
            self.load_indictts(language)
        
        try:
            from gtts import gTTS
            from pydub import AudioSegment
            import tempfile
            import os
            
            # Generate with gTTS
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Save to temporary MP3
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                tmp_path = tmp.name
            
            tts.save(tmp_path)
            
            # Convert to WAV
            audio = AudioSegment.from_mp3(tmp_path)
            
            # Convert to numpy
            samples = audio.get_array_of_samples()
            waveform = np.array(samples, dtype=np.float32)
            
            # Normalize
            if audio.channels == 2:
                waveform = waveform.reshape((-1, 2)).mean(axis=1)
            
            waveform = waveform / 32768.0
            sample_rate = audio.frame_rate
            
            # Clean up
            os.unlink(tmp_path)
            
            return waveform, sample_rate
            
        except ImportError:
            raise RuntimeError("gTTS not installed. Install with: pip install gtts pydub")
    
    def warmup_gpu(self) -> None:
        """Warm up GPU with dummy inference."""
        if self.device_type == "cuda" and torch.cuda.is_available():
            logger.info("[TTS] Warming up GPU...")
            try:
                # Load a model if available
                if "gu" not in self.mms_tts_models:
                    self.load_mms_tts("gu")
                
                # Run dummy inference
                dummy_text = "નમસ્તે"
                self._infer_mms_tts(dummy_text, "gu")
                
                # Clear cache
                torch.cuda.empty_cache()
                
                logger.info("[TTS] GPU warmup complete")
            except Exception as e:
                logger.warning(f"[TTS] GPU warmup failed: {e}")


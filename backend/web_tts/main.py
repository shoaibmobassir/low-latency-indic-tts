"""
FastAPI Web TTS Server
Main application entry point for Web TTS API on port 8050.
"""

import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.web_tts.dependencies import get_tts_engine
from backend.web_tts.router import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Gujarati & Marathi TTS API",
    description="Production-grade TTS API for Gujarati and Marathi languages",
    version="1.0.0"
)

# CORS configuration for frontend on port 3050
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3050", "http://127.0.0.1:3050"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Initialize TTS engine on startup."""
    logger.info("=" * 60)
    logger.info("Starting Web TTS Server on port 8050")
    logger.info("=" * 60)
    
    try:
        # Initialize engine (will pre-load models)
        engine = get_tts_engine()
        
        # Validate GPU availability
        logger.info(f"[TTS] Device: {engine.device_type} ({engine.device})")
        
        # Log loaded models
        logger.info(f"[TTS] MMS-TTS models loaded: {list(engine.mms_tts_models.keys())}")
        logger.info(f"[TTS] IndicTTS loaded: {engine.indictts_loaded}")
        
        logger.info("=" * 60)
        logger.info("Web TTS Server ready!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"[TTS] Startup failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("[TTS] Shutting down Web TTS Server...")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Gujarati & Marathi TTS API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "rest": "/api/tts",
            "websocket": "/api/ws/stream_tts",
            "health": "/api/health"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "backend.web_tts.main:app",
        host="0.0.0.0",
        port=8050,
        reload=False,
        log_level="info"
    )


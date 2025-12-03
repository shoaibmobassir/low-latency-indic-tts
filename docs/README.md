# 📚 TTS System Documentation

This directory contains all documentation for the Gujarati & Marathi TTS System project.

## Documentation Structure

### Core Documents

1. **[hooks.md](./hooks.md)** - Development hooks and pipeline protocols
2. **[phases.md](./phases.md)** - Complete implementation plan with 9 phases
3. **[protocols.md](./protocols.md)** - Strict development protocols and rules
4. **[product_requirements.md](./product_requirements.md)** - Complete product requirements
5. **[technical_requirements.md](./technical_requirements.md)** - Technical specifications and architecture
6. **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Dual-environment deployment guide (Mac/H100)
7. **[PHASE2_MASTER_PROMPT.md](./PHASE2_MASTER_PROMPT.md)** - Phase 2 implementation master prompt

## Quick Reference

### Current Status

- **Phase:** Phase 1 — Model Loading & Offline Testing ✅
- **Next Phase:** Phase 2 — GPU TTS Runtime Layer
- **Ports:** Backend 8050, Frontend 3050

### Key Requirements

- **Languages:** Gujarati, Marathi
- **Models:** MMS-TTS (Web UI), Piper TTS (Telecom API), IndicTTS (fallback)
- **Latency:** <100ms for all operations
- **Formats:** MP3/WAV (Web), PCM/G.711 (Telecom)
- **GPU Support:** CUDA (H100) for production, MPS (Mac) for development

### Critical Protocols

- ❌ NO placeholders or incomplete code
- ❌ NO hallucination (ask if unsure)
- ✅ Complete implementations only
- ✅ Strict port enforcement (8050, 3050)
- ✅ Follow exact project structure

## Usage

Before starting any phase, review:

1. **hooks.md** - Understand the hooks to follow
2. **phases.md** - Know the current and next phase
3. **protocols.md** - Ensure compliance with all protocols
4. **product_requirements.md** - Verify feature requirements
5. **technical_requirements.md** - Check technical specifications

## Phase Execution

Each phase must:

1. Follow all hooks (see [hooks.md](./hooks.md))
2. Adhere to all protocols (see [protocols.md](./protocols.md))
3. Deliver complete, production-ready code
4. Meet all product requirements (see [product_requirements.md](./product_requirements.md))
5. Comply with technical specifications (see [technical_requirements.md](./technical_requirements.md))

## Phase-Specific Guides

### Phase 2 Implementation

When starting Phase 2, use the **Phase 2 Master Prompt**:

1. Open [`PHASE2_MASTER_PROMPT.md`](./PHASE2_MASTER_PROMPT.md)
2. Copy the entire prompt
3. Paste it into Cursor before starting Phase 2
4. Follow the prompt's instructions exactly

The master prompt ensures:
- ✅ Correct model paths from Phase 1
- ✅ Proper device detection (CUDA/MPS/CPU)
- ✅ No placeholders or incomplete code
- ✅ Full implementation of TTS engine
- ✅ Compliance with all protocols

---

**Last Updated:** Phase 1 Complete
**Status:** Ready for Phase 2


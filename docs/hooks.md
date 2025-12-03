# 🔗 Development Hooks & Pipeline Protocol

This document defines the hooks and protocols that Cursor must follow throughout all development phases.

## Hook A — Phase Recall

**Before executing any future task, Cursor must restate:**

- Current phase
- Next phase
- What the deliverable is
- What files will be created

**Example:**
```
Current Phase: Phase 1 — Model Loading & Offline Testing
Next Phase: Phase 2 — GPU TTS Runtime Layer
Deliverable: Functional model loading scripts for XTTS-v2 and Piper TTS
Files to Create: backend/models/xtts_loader.py, backend/models/piper_loader.py, backend/models/__init__.py
```

## Hook B — Dependency Completion Check

**Before proceeding, Cursor must check:**

- Are all prior required files created?
- Are all imports resolvable?
- Are all model paths correct?
- Are all dependencies installed?

**If incomplete → request user clarification before proceeding.**

## Hook C — Strict Diff Mode

**When updating existing code, Cursor must:**

- Produce minimal, clean, accurate diffs
- Only modify what is necessary
- Preserve existing functionality
- Maintain code style consistency

## Hook D — No Implicit Optimization

**Cursor must NOT:**

- Refactor unrelated code
- "Improve" architecture without explicit request
- Guess future implementation needs
- Add features not in the current phase scope

## Hook E — Model Safety

**Before using TTS models, Cursor must:**

- Confirm model paths are correct
- Confirm GPU availability (if required)
- Confirm correct inference code matches actual model APIs
- Verify model format compatibility (ONNX, PyTorch, etc.)

## Hook F — Port Enforcement

**Cursor must enforce port requirements:**

- **Backend (web_tts + telecom_tts): port 8050**
- **Frontend (Next.js): port 3050**

**Applied to:**
- Dockerfile configurations
- docker-compose.yml
- FastAPI app startup
- WebSocket URLs
- Next.js frontend environment variables
- API endpoint configurations

## Hook G — File Creation Protocol

**When creating a file, Cursor must:**

1. State: `"Creating file: <path>"`
2. Write complete and exact file content
3. Include all necessary imports
4. Provide full class/function implementations
5. No placeholders, TODOs, or stubs

## Hook H — Communication Protocol

**When generating code:**

- Clearly state file creation
- Provide zero explanatory text after code blocks unless asked
- Do NOT merge multiple files into one generation unless explicitly instructed
- Use minimal, focused responses


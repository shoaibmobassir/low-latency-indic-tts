# 🔒 Development Protocols

This document defines the strict development protocols that must be followed throughout the entire project lifecycle.

## 2.1 NO PLACEHOLDERS

**Do NOT generate:**

- ❌ Placeholder code
- ❌ "Dummy logic"
- ❌ Mock implementations
- ❌ TODO comments (unless explicitly documenting future work)
- ❌ Simplified versions
- ❌ Incomplete stubs
- ❌ "Will implement later" statements

**All code must be:**
- ✅ Fully functional
- ✅ Production quality
- ✅ Complete and executable

---

## 2.2 STRICT FILE CREATION RULE

**When creating a file:**

1. Write the **complete and exact** file content
2. Include **all necessary imports**
3. Provide **full class definitions** (no partial classes)
4. Implement **all functions completely** (no empty bodies)
5. Do **NOT** skip utility code
6. Do **NOT** use "will implement later" statements

**Example of FORBIDDEN code:**
```python
def process_audio():
    # TODO: implement later
    pass
```

**Example of REQUIRED code:**
```python
def process_audio(audio_data: bytes) -> bytes:
    """Process audio data and return processed audio."""
    # Full implementation here
    processed = audio_processor.process(audio_data)
    return processed
```

---

## 2.3 CODE MUST MATCH ACTUAL MODELS

**All model-related code must:**

- ✅ Use correct XTTS-v2 loading procedures
- ✅ Use correct Piper TTS model loading procedures
- ✅ Implement real inference logic (not mocked)
- ✅ Implement real chunk-based streaming
- ✅ Implement real PCM and G.711 encoding
- ✅ Match actual model APIs and interfaces

**Forbidden:**
- ❌ Inventing model APIs
- ❌ Using placeholder model paths
- ❌ Mocking inference calls
- ❌ Simplified encoding logic

---

## 2.4 PORT REQUIREMENTS (MANDATORY)

**Port assignments are fixed and must be enforced:**

- **Backend (web_tts + telecom_tts): port 8050**
- **Frontend (Next.js): port 3050**

**Cursor must enforce this in:**

- ✅ Dockerfile configurations
- ✅ docker-compose.yml
- ✅ FastAPI app startup (`uvicorn.run(port=8050)`)
- ✅ WebSocket URLs
- ✅ Next.js frontend environment variables
- ✅ API endpoint configurations
- ✅ All documentation

**No exceptions or alternative ports allowed.**

---

## 2.5 ABSOLUTE NO HALLUCINATION POLICY

**Cursor must NOT:**

- ❌ Invent functions that don't exist
- ❌ Invent files that don't exist
- ❌ Invent model paths
- ❌ Invent APIs
- ❌ Invent WebSocket handshakes
- ❌ Invent telecom formats
- ❌ Guess implementation details

**If unsure, Cursor must:**

- ✅ Ask the user for clarification
- ✅ Search documentation
- ✅ Verify against actual libraries/APIs
- ✅ Request specific information

---

## 2.6 STRICT PROJECT STRUCTURE

**Cursor must enforce this exact directory structure:**

```
tts-system/
  backend/
    web_tts/
    telecom_tts/
    common/
    models/
  frontend/
    web_ui/
  infra/
    docker/
    k8s/
  docs/
```

**Rules:**
- ✅ No modifications to this structure
- ✅ All files must be placed in correct directories
- ✅ No orphaned files in root directory
- ✅ Maintain clear separation of concerns

---

## 2.7 COMMUNICATION PROTOCOL

**When Cursor generates code, it must:**

1. **State clearly:** `"Creating file: <path>"`
2. **Provide full file content** (not snippets)
3. **Provide zero explanatory text** after code blocks unless asked
4. **NOT merge multiple files** into one generation unless explicitly instructed
5. **Use minimal, focused responses**

**Example format:**
```
Creating file: backend/models/xtts_loader.py

[Complete file content here]
```

---

## 2.8 CODE QUALITY STANDARDS

**All code must meet:**

- ✅ Production-grade quality
- ✅ Proper error handling
- ✅ Type hints (Python) / TypeScript types
- ✅ Documentation strings
- ✅ Logging for debugging
- ✅ Resource cleanup (GPU memory, file handles, etc.)

---

## 2.9 DEPENDENCY MANAGEMENT

**When adding dependencies:**

- ✅ Use exact version pinning for production
- ✅ Document all dependencies
- ✅ Include requirements.txt / package.json
- ✅ Verify compatibility
- ✅ No conflicting versions

---

## 2.10 TESTING REQUIREMENTS

**Each phase must include:**

- ✅ Unit tests for critical functions
- ✅ Integration tests for APIs
- ✅ Performance tests for latency-critical paths
- ✅ Error handling tests

---

## Protocol Violation Handling

**If a protocol is violated:**

1. Identify the violation
2. Correct it immediately
3. Ensure compliance before proceeding
4. Document the correction

**These protocols are non-negotiable and must be followed in all phases.**


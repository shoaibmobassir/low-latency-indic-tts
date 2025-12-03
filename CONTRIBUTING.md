# Contributing to Indic TTS Streaming

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/yourusername/indic-tts-streaming.git
   cd indic-tts-streaming
   ```
3. **Set up development environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r backend/models/requirements.txt
   cd frontend/web_ui && npm install && cd ../..
   ```

## 📋 Development Guidelines

### Code Style

**Python**
- Follow [PEP 8](https://pep8.org/)
- Use type hints where applicable
- Maximum line length: 100 characters
- Use descriptive variable names

**TypeScript/JavaScript**
- Use TypeScript for all new code
- Follow ESLint configuration
- Use functional components with hooks
- Prefer `const` over `let`

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add Hindi language support
fix: resolve WebSocket connection timeout
docs: update API documentation
refactor: optimize audio chunking logic
test: add unit tests for language detection
```

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

## 🧪 Testing

### Before Submitting

1. **Run tests** (if available)
   ```bash
   pytest backend/
   ```

2. **Test manually**
   - Start servers: `./start_servers.sh`
   - Test Gujarati text: "નમસ્તે, તમે કેમ છો?"
   - Test Marathi text: "नमस्कार, तुम्ही कसे आहात?"
   - Test WebSocket streaming
   - Test REST API

3. **Check for linting errors**
   ```bash
   # Python
   flake8 backend/
   
   # TypeScript
   cd frontend/web_ui && npm run lint
   ```

## 📝 Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, commented code
   - Update documentation if needed
   - Add tests for new features

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request**
   - Provide a clear description of changes
   - Reference any related issues
   - Include screenshots/videos if UI changes

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Tests pass (if applicable)
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No unnecessary files included
- [ ] PR description is complete

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Description**: Clear description of the issue
2. **Steps to Reproduce**: Numbered steps to reproduce
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**:
   - OS (macOS, Linux, Windows)
   - Python version
   - Node.js version
   - GPU (CUDA, MPS, CPU)
6. **Logs**: Relevant error messages or logs

## 💡 Suggesting Features

Feature requests are welcome! Please include:

1. **Use Case**: Why is this feature needed?
2. **Proposed Solution**: How should it work?
3. **Alternatives**: Other solutions considered
4. **Additional Context**: Screenshots, examples, etc.

## 🌏 Adding New Languages

To add support for a new Indic language:

1. **Check model availability**
   - MMS-TTS: https://huggingface.co/facebook
   - IndicTTS: https://github.com/AI4Bharat/Indic-TTS

2. **Update configuration**
   ```python
   # backend/common/config.py
   MMS_TTS_HI_MODEL = "facebook/mms-tts-hin"  # Hindi
   ```

3. **Add language detection**
   ```python
   # backend/common/language_detection.py
   HINDI_RANGES = [(0x0900, 0x097F)]  # Devanagari
   ```

4. **Update frontend**
   ```typescript
   // frontend/web_ui/components/LanguageSelector.tsx
   { value: 'hi', label: 'हिन्दी (Hindi)' }
   ```

5. **Test thoroughly** with native text

6. **Update documentation**

## 📚 Documentation

When updating documentation:

- Keep it clear and concise
- Include code examples
- Use proper Markdown formatting
- Add screenshots for UI changes
- Update table of contents if needed

## ⚡ Performance Optimization

When optimizing performance:

1. **Measure first**: Use profiling tools
2. **Document changes**: Explain the optimization
3. **Benchmark**: Include before/after metrics
4. **Test thoroughly**: Ensure no regressions

## 🤝 Community

- Be respectful and constructive
- Help others when possible
- Follow the [Code of Conduct](CODE_OF_CONDUCT.md)
- Share knowledge and learn together

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Indic TTS Streaming! 🎙️


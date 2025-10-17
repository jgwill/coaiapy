# Contributing to coaiapy-mcp

Thank you for your interest in contributing to coaiapy-mcp! This document provides guidelines for contributing to the project.

## 🎯 Project Goals

coaiapy-mcp aims to provide a clean, type-safe MCP (Model Context Protocol) wrapper around coaiapy's observability toolkit. Our focus is on:

1. **Simplicity**: Easy-to-use tools for LLMs
2. **Reliability**: Robust error handling and graceful degradation
3. **Maintainability**: Clean code with comprehensive tests
4. **Documentation**: Clear examples and usage guides

## 🚀 Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- Redis (for integration tests)
- Langfuse account (for integration tests)

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jgwill/coaiapy.git
   cd coaiapy/coaiapy-mcp
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Set up environment variables** (for integration tests):
   ```bash
   export LANGFUSE_SECRET_KEY="sk-lf-..."
   export LANGFUSE_PUBLIC_KEY="pk-lf-..."
   export LANGFUSE_HOST="https://cloud.langfuse.com"
   ```

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_prompts.py

# Run with coverage
pytest --cov=coaiapy_mcp tests/

# Run only unit tests (no external dependencies)
pytest -m unit

# Run integration tests (requires Redis and Langfuse)
pytest -m integration
```

## 📝 Code Style

We follow PEP 8 guidelines with these specifics:

- **Line length**: 100 characters maximum
- **Docstrings**: Google-style docstrings for all public functions
- **Type hints**: Use type hints for function parameters and returns
- **Async/await**: All tool functions must be async for MCP compliance

### Example Function

```python
async def coaia_example_tool(
    param1: str,
    param2: Optional[int] = None
) -> Dict[str, Any]:
    """
    Brief description of what the tool does.
    
    Args:
        param1: Description of param1
        param2: Optional description of param2
        
    Returns:
        Dict with success status and result data
    """
    # Implementation here
    return {"success": True, "data": "result"}
```

## 🔧 Adding New Tools

To add a new MCP tool:

1. **Add tool function to `tools.py`**:
   ```python
   async def coaia_new_tool(arg1: str) -> Dict[str, Any]:
       """Tool description"""
       cmd = ["coaia", "command", arg1]
       result = subprocess.run(cmd, capture_output=True, text=True, check=False)
       
       if result.returncode == 0:
           return {"success": True, "output": result.stdout}
       else:
           return {"success": False, "error": result.stderr}
   ```

2. **Register in TOOLS dict** (end of `tools.py`):
   ```python
   TOOLS = {
       # ... existing tools
       "coaia_new_tool": coaia_new_tool,
   }
   ```

3. **Add tool registration in `server.py`**:
   ```python
   Tool(
       name="coaia_new_tool",
       description="Description of new tool",
       inputSchema={
           "type": "object",
           "properties": {
               "arg1": {"type": "string", "description": "Argument description"}
           },
           "required": ["arg1"]
       }
   )
   ```

4. **Write tests** in `tests/test_tools.py`:
   ```python
   @pytest.mark.asyncio
   async def test_new_tool():
       result = await coaia_new_tool("test_value")
       assert "success" in result
   ```

5. **Update documentation**:
   - Add to README.md tools table
   - Add to USAGE_EXAMPLES.md with example usage

## 📚 Adding New Prompts

To add a new prompt template:

1. **Add to PROMPTS dict in `prompts.py`**:
   ```python
   PROMPTS = {
       # ... existing prompts
       "new_prompt_id": {
           "name": "Prompt Display Name",
           "description": "What this prompt helps with",
           "arguments": [
               {
                   "name": "arg1",
                   "description": "Argument description",
                   "required": True
               }
           ],
           "template": """
   Prompt template with {arg1} placeholders
           """
       }
   }
   ```

2. **Write tests** in `tests/test_prompts.py`:
   ```python
   def test_new_prompt():
       prompt = get_prompt("new_prompt_id")
       assert prompt is not None
       
       rendered = render_prompt("new_prompt_id", arg1="value")
       assert "value" in rendered
   ```

3. **Update documentation**:
   - Add to README.md prompts section
   - Add usage example to USAGE_EXAMPLES.md

## 🔍 Pull Request Process

1. **Fork the repository** and create a feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Make your changes**:
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation

3. **Run tests** to ensure nothing breaks:
   ```bash
   pytest
   ```

4. **Commit your changes**:
   ```bash
   git commit -m "Add amazing feature"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Open a Pull Request**:
   - Provide clear description of changes
   - Reference any related issues
   - Ensure CI tests pass

## 🐛 Reporting Issues

When reporting issues, please include:

1. **Description**: Clear description of the problem
2. **Steps to reproduce**: Minimal steps to reproduce the issue
3. **Expected behavior**: What you expected to happen
4. **Actual behavior**: What actually happened
5. **Environment**:
   - Python version
   - Operating system
   - coaiapy-mcp version
   - coaiapy version

## 💡 Feature Requests

We welcome feature requests! Please:

1. **Check existing issues** to avoid duplicates
2. **Describe the feature** and its benefits
3. **Provide use cases** showing how it would be used
4. **Consider implementation** (optional but helpful)

## 🎨 Good First Issues

Looking for a place to start? Check out issues labeled:
- `good-first-issue` - Easy issues for beginners
- `documentation` - Documentation improvements
- `enhancement` - New features or improvements

## 📋 Project Phases

We're following a phased development approach:

- **Phase 1** (✅ Complete): Core Langfuse observability tools
- **Phase 2** (Planned): Pipeline automation tools
- **Phase 3** (Planned): Audio processing tools

See ROADMAP.md for details on upcoming features.

## 🤝 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help create a welcoming environment

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT).

## 🙏 Recognition

Contributors will be recognized in:
- GitHub contributors page
- Release notes
- Project documentation (for significant contributions)

## 📞 Questions?

- **Issues**: https://github.com/jgwill/coaiapy/issues
- **Discussions**: https://github.com/jgwill/coaiapy/discussions

Thank you for contributing to coaiapy-mcp! 🎉

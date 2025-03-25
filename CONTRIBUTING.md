# Contributing to SURF

Thank you for your interest in contributing to SURF! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to uphold our Code of Conduct, which expects all participants to treat each other with respect and professionalism.

## How Can I Contribute?

### Reporting Bugs

1. Before submitting a bug report, please check if the issue has already been reported.
2. Use the bug report template and provide all the requested information.
3. Include detailed steps to reproduce the bug.
4. Include relevant logs and error messages.
5. Describe what you expected to happen and what actually happened.

### Suggesting Enhancements

1. Check if your idea has already been suggested.
2. Use the feature request template and provide all the requested information.
3. Describe the enhancement you're suggesting in detail.
4. Explain why this enhancement would be useful to most SURF users.

### Code Contributions

#### Local Development Setup

1. Fork the repository.
2. Clone your fork locally:
   ```
   git clone https://github.com/44za12/surf.git
   cd surf
   ```
3. Set up the development environment:
   ```
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install fastapi uvicorn aiohttp python-dotenv beautifulsoup4 markdown pytest
   ```
4. Create a branch for your changes:
   ```
   git checkout -b feature/your-feature-name
   ```

#### Making Changes

1. Follow the coding style and conventions used in the project.
2. Write or update tests for your changes.
3. Document your changes (docstrings, comments, update README if necessary).
4. Ensure all tests pass:
   ```
   pytest
   ```

#### Submitting a Pull Request

1. Push your changes to your fork:
   ```
   git push origin feature/your-feature-name
   ```
2. Submit a pull request to the main repository.
3. Follow the pull request template and provide all the requested information.
4. Wait for a maintainer to review your pull request.
5. Make any requested changes and update your pull request.

## Style Guides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests after the first line

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code style. Additionally:

* Use 4 spaces for indentation (not tabs)
* Use docstrings for all modules, classes, and functions
* Type hints are encouraged
* Line length should be limited to 88 characters (compatible with Black)

### Documentation Style Guide

* Use Markdown for documentation
* Keep documentation up-to-date with code changes
* Be clear and concise
* Include examples where appropriate

## Project Structure

The project is structured as follows:

```
app/
├── api/           # API route handlers
├── core/          # Core configuration
├── utils/         # Utility functions
├── main.py        # Main FastAPI application
docs/              # Documentation
tests/             # Tests
```

## Testing

We use pytest for testing. All code contributions should include appropriate tests.

To run the tests:

```
pytest
```

## Documentation

We encourage improvements to the documentation. If you find something unclear or missing, please submit a pull request with your improvements.

## Questions?

If you have any questions about contributing, please open an issue or reach out to the maintainers.

Thank you for contributing to SURF! 
# Network Evaluation Service Guidelines

## Build & Run Commands
- Run ping test: `python backend/pingTest.py`
- Install dependencies: `pip install -r requirements.txt` (create this file for dependencies)
- Create venv: `python -m venv venv && source venv/bin/activate`

## Code Style Guidelines
- **Formatting**: Follow PEP 8 standards for Python code
- **Imports**: Group standard library imports first, then third-party, then local
- **Typing**: Add type hints to function parameters and return values
- **Naming**: 
  - snake_case for variables and functions
  - CamelCase for classes
  - UPPER_CASE for constants
- **Error Handling**: Use try/except blocks with specific exceptions
- **Documentation**: Add docstrings to all functions using """ """ format
- **Line Length**: Maximum 88 characters per line
- **Testing**: Write unit tests for new functions in a separate tests directory
- **Linting**: Run `flake8 backend` before committing changes
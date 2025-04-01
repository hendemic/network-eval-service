# Network Evaluation Service Guidelines

## Build & Run Commands
- Run ping test: `python backend/pingTest.py`
- Run network test: `python backend/run_test.py`
- Initialize database: `python backend/db_init.py`
- Start Flask application: `python -m backend.app`
- Install dependencies: `pip install -r requirements.txt` (create this file for dependencies)
- Create venv: `python -m venv venv && source venv/bin/activate`
- The project is hosted at: `https://github.com/hendemic/network-eval-service`

## Code Style Guidelines

### Backend (Python)
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

### Frontend
- **Vue Components**: Use PascalCase naming (NetworkMetric, ThemeToggle)
- **JavaScript**: 
  - camelCase for variables/functions
  - PascalCase for components/classes
  - 'use' prefix for composables (useChartData)
- **CSS Conventions**:
  - Functional variable naming (--color-brand-primary, --color-text-secondary)
  - Separate CSS into logical files (theme, base, components, etc.)
  - Support dark mode via .dark-theme class
  - Use scoped CSS in components

## Project Structure

### Backend
- `backend/`: Core application code
  - `app.py`: Flask application and API routes
  - `models.py`: Database models using SQLAlchemy
  - `config.py`: Configuration settings
  - `pingTest.py`: Network measurement tools
  - `run_test.py`: CLI to execute and save tests
  - `db_init.py`: Database initialization
- `tests/`: Testing infrastructure
  - `unit-tests/`: Unit test modules
  - `end-to-end-tests/`: E2E test modules

### Frontend
- `src/components`: Reusable Vue components
- `src/views`: Page components
- `src/composables`: Reusable logic
- `src/store`: Vuex state management
- `src/services`: API services
- `src/assets/css`: Organized CSS files

## Database Management
- SQLAlchemy ORM with Flask-SQLAlchemy integration
- Schema-aware table configuration for PostgreSQL
- Migration support via Flask-Migrate

## Configuration Patterns
- Environment variable configuration for settings
- Configuration class hierarchy (Base, Development, Production, Testing)
- Test-specific SQLite configuration
# FastAPI Template

An opinionated FastAPI template with a structured approach to building backend applications. This template incorporates best practices from personal experience and the FastAPI community, heavily inspired by [this excellent repository](https://github.com/zhanymkanov/fastapi-best-practices).

## Environment & Package Management

This repository uses `uv` for fast package and environment management. The structure is compatible with Poetry, but requires adjustments to `pyproject.toml`.

The application is packaged as the `backend` module. You can customize both the folder name and package parameters in `pyproject.toml`.

## Project Structure

```
fastapi-template/
├── alembic/                    # Database migrations
├── deploy/                     # Deployment configurations
│   ├── docker-compose.yaml
│   ├── init_db.sh
│   └── init_db.sql
├── docs/                       # Developer and LLM documentation
│   ├── fastapi.md             # FastAPI conventions
│   ├── schemas.md             # Pydantic schema patterns
│   ├── sqlalchemy.md          # SQLAlchemy model conventions
│   └── new_feature_workflow.md # Step-by-step feature creation guide
├── src/
│   └── backend/               # Main application package
│       ├── db/                # Database layer
│       │   ├── db.py         # Base class and DatabaseManager
│       │   ├── mixins.py     # Reusable model mixins
│       │   ├── models/       # SQLAlchemy models
│       │   └── init_db.py    # Database initialization
│       ├── agents/             # AI agents and agentic workflows
│       ├── clients/            # External service integrations
│       ├── users/             # Example feature module
│       │   ├── routes.py     # API endpoints
│       │   ├── schemas.py    # Pydantic models
│       │   ├── service.py    # Business logic
│       │   ├── repository.py # Data access layer
│       │   └── exceptions.py # Feature-specific exceptions
│       ├── config.py          # Application configuration
│       ├── dependencies.py    # Shared dependencies (e.g., get_db_session)
│       ├── schemas.py         # Base Pydantic models
│       └── server.py          # FastAPI app creation
├── templates/                  # Template files
├── config.yaml                 # Application configuration
├── pyproject.toml             # Project dependencies
└── alembic.ini                # Alembic configuration
```

### Feature Organization

Features are organized into self-contained modules under `src/backend/`. Each feature contains:
- `routes.py` - API endpoints
- `schemas.py` - Pydantic models for request/response validation
- `service.py` - Business logic
- `repository.py` (optional) - Object-oriented data access layer
- `exceptions.py` - Feature-specific HTTP exceptions

The `src/backend/` structure allows for future expansion with additional modules like a Streamlit frontend or separate frontend application.

## Documentation

The `docs/` folder contains comprehensive documentation for developers and LLMs:

- **`fastapi.md`** - FastAPI conventions, route patterns, and service layer guidelines
- **`schemas.md`** - Pydantic schema conventions and validation patterns
- **`sqlalchemy.md`** - SQLAlchemy model conventions and available mixins
- **`clients.md`** - External service client patterns and best practices
- **`new_feature_workflow.md`** - Complete checklist for adding new features

Documentation follows the same modular structure as the backend code.

## Configuration

The template includes a flexible configuration system that supports YAML files:

- Application settings can be defined in `config.yaml` with comments
- Secret fields are protected by pre-commit hooks and cannot be committed in YAML files
- Store secrets in `.env` files or your environment manager (e.g., Railway, AWS Secrets Manager)

**Example deployment workflow:**
1. Point your deployment to a specific `config.yaml` file
2. Load secrets through the platform's environment variable system

## Testing Philosophy

This template follows a testing drawn from experience.
In general, unit testing is not really useful for API development, since most of the API calls are a chaining of simple operations.
I personally despise mocks, but I understand their use cases.

### Unit Tests
**Runtime:** Milliseconds
**Purpose:** Test isolated, pure functions / classes without external dependencies

- Test simple, self-contained components (e.g., string validators, calculators)
- Avoid mocking when possible
- If a component requires a database session, use integration tests instead

**Objective:** Ensure individual functions work correctly and prevent regressions

### Integration Tests
**Runtime:** Seconds
**Purpose:** Test business logic with real database connections

- Test `service.py` and `repository.py` with actual database connections
- Test `routes.py` using FastAPI's test client (no server required)
- Mock only external dependencies (APIs, third-party services)
- Verify both application logic and database state
- Focus on error handling when external dependencies fail

**Objective:** Ensure features work correctly end-to-end and maintain functional consistency

### End-to-End Tests
**Runtime:** Seconds to minutes
**Purpose:** Test complete user workflows from an external perspective

- Treat the application as a black box (no access to internal state)
- Database access allowed for verification only
- No mocking
- Cover complex, multi-step workflows requested by business stakeholders
- Run after deployment to verify application integrity

**Objective:** Ensure the application meets business requirements in production-like conditions

### Fuzzy Tests
**Runtime:** Minutes
**Purpose:** Test application robustness with random inputs

- Generate random inputs to explore multiple code paths
- Useful when test cases are easy to generate programmatically
- Focus on statistical properties rather than specific behaviors
- Can be applied at any test level (unit, integration, or E2E), while respecting their requirements

**Objective:** Discover edge cases and ensure system stability under unexpected inputs

### Performance Tests
**Runtime:** heavily dependent
**Purpose:** Measure system performance under load and identify bottlenecks

- Test response times, throughput, and resource utilization under various load conditions
- Identify performance degradation points (e.g., database query optimization, caching needs)
- Benchmark critical endpoints to establish performance baselines
- Simulate realistic traffic patterns and concurrent user scenarios
- Monitor memory usage, CPU utilization, and database connection pools

**Objective:** Ensure the application meets performance requirements and scales appropriately under production load

## AI Agents

The `src/backend/agents/` folder contains AI agents and agentic workflows. Agents are autonomous components that can.

In the future, dedicated folders may be added for AI models and datasets as the project scales.

## External Service Integrations

The `src/backend/clients/` folder contains wrappers for external services and libraries. These clients provide a clean abstraction layer for:

- **Third-party APIs** - Payment processors, email services, SMS providers
- **AI/ML services** - OpenAI, Anthropic
- **Cloud services** - AWS S3, Google Cloud Storage, Azure services
- **Other external dependencies** - Search engines, analytics platforms

Clients encapsulate authentication, error handling, and retry logic, making external integrations easier to test and maintain.

See `docs/clients.md` for detailed conventions and examples.

## Quick Start

### Run a sample server
```
cp .env.example .env
docker-compose up --build
```

### Add new features

See `docs/new_feature_workflow.md` for a complete guide on adding new features to the application.

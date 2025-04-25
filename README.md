# Profile Matcher

## Overview

A monorepo containing stateless Python microservices for campaign management and profile management, designed for high scalability and type safety using FastAPI and Pydantic.

This project follows modern FastAPI best practices:
- Modular endpoints using `APIRouter` and separate files for each logical group of endpoints.
- Dependency injection is handled via dedicated provider functions in `services/profiles/dependencies.py`.
- Business logic and data access are separated into class-based service and repository layers.
- Application state (such as the MongoDB client) is accessed via the FastAPI `Request` object.
- Testing uses FastAPI's dependency override system for clean, maintainable test doubles (no monkeypatching required).
- The codebase is organized for scalability, maintainability, and ease of extension.

## Project Structure & Architecture

```
services/
  profiles/
    api/
      __init__.py
      health.py           # Health check endpoints (router)
      client_config.py    # Client config endpoints (router)
    main.py               # App creation, lifespan, router registration
    dependencies.py       # Dependency providers for dependency injection
    service.py            # ProfileService: core business logic
    repository/
      profiles.py         # ProfileRepository: profile DB access
      campaigns.py        # CampaignRepository: campaign API access
  campaigns/
    ...
```

- **Endpoints** are grouped by domain in `services/profiles/api/`, each as a router. Routers are registered in `main.py`.
- **Dependency Injection** is centralized in `dependencies.py` and uses FastAPI's DI system.
- **Repositories** and **services** are class-based and injected via DI, making the codebase testable and extensible.
- **MongoDB client** is attached to FastAPI app state and accessed via the `Request` object in dependencies.
- **Testing** uses dependency overrides for injecting mocks/stubs.

## Running Tests

Make sure all dependencies are installed. If you need to install dependencies, run:

```bash
uv sync
```

To run the tests, use:

```bash
pytest
```

To produce a coverage report:

```bash
uv run pytest --cov --cov-report=xml --cov-report=term-missing
```

## Services

- **Campaign Service**: Serves campaign data via HTTP API.
- **Profile Service**: Serves player profiles enriched with active campaings matching the player profile.

## Development with Docker Compose

To start both services for local development:

```bash
docker compose up --build
```

### Live Code Reloading

The `docker-compose.yml` mounts the local `./services/campaigns` and `./services/profiles` directories into their respective containers at `/app/services/campaigns` and `/app/services/profiles`. This enables live code reloading and development without rebuilding the image. Any code changes you make locally will be reflected immediately in the running containers.

### Ports

- Campaigns service: [http://localhost:54325](http://localhost:54325)
- Profiles service: [http://localhost:54326](http://localhost:54326)

## Adding Dependencies

Install Python dependencies using `uv` in the root directory, then restart the containers:

```bash
uv add <package>
docker compose restart
```

## Notes
- See `SPEC.md` for architectural details and principles.

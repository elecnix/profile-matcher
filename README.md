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

## System Architecture

This project consists of two stateless Python microservices:
- **Campaign Service**: Serves campaign definitions via an HTTP API.
- **Profile Service**: Handles player profile lookups, campaign matching, and serves enriched client configurations.

Both services are built with FastAPI and Pydantic for high performance, type safety, and modern Python best practices.

## Service Responsibilities

- **Campaign Service**
  - Exposes a `/campaigns` endpoint returning all active campaigns, each with eligibility matchers (level, country, inventory, etc.).
  - Designed for a small number of campaigns that change infrequently.

- **Profile Service**
  - Loads player profiles from MongoDB.
  - Fetches and caches campaign data from the Campaign Service.
  - Matches campaigns to players using composable matcher utilities.
  - Serves the resulting configuration via `/get_client_config/{player_id}`.
  - Health check endpoint for an eventual deployment to Kubernetes.

## Data Flow

1. The client requests their configuration from the Profile Service.
2. The Profile Service loads the player profile from MongoDB.
3. It retrieves (and caches) the list of campaigns from the Campaign Service.
4. Matcher utilities evaluate which campaigns the player is eligible for.
5. The enriched profile, including active campaigns, is returned to the client.

## Campaign Caching

- The Profile Service caches campaign data in memory (5 min TTL) to optimize performance, as campaigns are few and change rarely, but profile lookups are frequent.
- This reduces load on the Campaign Service and improves response times.
- In the future, a cache invalidation endpoint can be added, allowing the Profile Service or an external system to immediately expire the cache when campaigns change.

## Extensibility

- **Modular Structure**: Endpoints are grouped by domain and registered as routers, making it easy to add new API routes.
- **Dependency Injection**: All service and repository dependencies are injected, enabling easy testing and extension.
- **Type Safety**: All data models are typed with Pydantic, ensuring robust validation and maintainability.
- **Testability**: The architecture supports isolated unit testing and full integration testing with dependency overrides.

## Test Strategy

- **Unit Tests**: Repository and matcher logic are tested in isolation using mocks.
- **Integration Tests**: API endpoints are tested with FastAPI's `TestClient` and dependency injection.
- **Property-Based Testing**: Hypothesis is used to generate diverse and realistic test data, ensuring correctness across a wide range of inputs, and removing the need for explicit and repetitive object creation boilerplate.
- **Mocking**: All external dependencies (database, HTTP) are mocked for deterministic, fast tests.
- **Coverage**: Tests cover repository logic, service/matcher logic, and API endpoints, including error paths.

## Rationale

- **Performance**: Caching and modularity ensure the system is scalable and efficient for high-frequency profile lookups.
- **Maintainability**: Clear separation of concerns and strong typing make the codebase easy to extend and refactor.
- **Future-Proofing**: The architecture is designed to support new features, endpoints, and integrations with minimal friction.

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
docker compose restart --build -d
```

## Notes
- See `SPEC.md` for architectural details and principles.

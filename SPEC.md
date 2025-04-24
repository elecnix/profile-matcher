# SPEC.md

## Goals

- Build a stateless Profile Matcher service in Python that can evaluate and update player profiles based on active campaigns.
- Ensure the service is type-safe, fast, and scalable to support millions of profiles and hundreds of campaigns.
- Enable realistic component testing with Docker and support efficient local and CI-based development workflows.

## Principles

- **Stateless Services**: All services (matcher, profile-service, campaign-service) are stateless and can be scaled horizontally.
- **Type Safety**: Use Pydantic and modern Python typing to ensure strict validation and safe refactoring.
- **Component Isolation**: Each service has a clear contract and can be tested independently via HTTP APIs.
- **Performance through Caching**: Campaigns are cached locally within each matcher instance to reduce MongoDB load.
- **Realistic Testing**: Component tests should validate integration across real containers, not just mocks.
- **Fast Feedback Loop**: Mocks (e.g., with respx) and in-process FastAPI apps are used for rapid test iterations.

## Architectural Decisions

- **Python + FastAPI**: Chosen for speed, type-safety, and ease of async HTTP integration.
- **MongoDB**: Used for storing player profiles due to flexibility and scalability.
- **Campaign Matching in App**: Matching logic is computed in the matcher app using cached campaigns.
- **Campaign Service**: Returns static or preconfigured campaign data, does not persist state.
- **Profile Service**: Provides CRUD operations on profiles, designed to facilitate test seeding.
- **Docker Compose**: Used for local and CI test orchestration (matcher, MongoDB, profile, and campaign services).
- **Component Test Strategy**:
  - Realistic tests spin up actual containers and seed data through HTTP.
  - Lightweight tests use mocked HTTP and in-memory stores for speed.
- **No Service Discovery for Now**: Services communicate via static Docker Compose DNS hostnames.
- **Future-Proofing**: Design allows plugging in pub/sub or service mesh features later without major refactor.


# Profile Matcher

## Overview

A monorepo containing stateless Python microservices for campaign management and profile management, designed for high scalability and type safety using FastAPI and Pydantic.

## Services

- **Campaign Service**: Serves campaign data via HTTP API.
- **Profile Service**: Serves player profiles enriched with active campaings matching the player profile.

## Development with Docker Compose

To start both services for local development:

```bash
uv sync
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

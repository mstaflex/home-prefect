# home-prefect

Home network automation and orchestration using [Prefect 3](https://docs.prefect.io).

Flows run on a central home server (or inside Docker) and remote workers run on
thin clients such as Raspberry Pi devices to interact with local hardware.

---

## Project structure

```
home-prefect/
├── src/home_prefect/
│   ├── config/          # pydantic-settings configuration
│   ├── flows/           # Prefect flows  (add new automation here)
│   ├── tasks/           # Reusable Prefect tasks
│   └── deployments/     # Deployment definitions (schedules, work pools)
├── tests/               # pytest test suite
├── docker/
│   ├── docker-compose.yml   # postgres + prefect-server + worker
│   ├── Dockerfile.server    # custom server image (optional)
│   └── Dockerfile.worker    # worker image
├── .devcontainer/       # VS Code devcontainer (Windows-friendly)
├── scripts/             # helper shell scripts
├── pyproject.toml       # Poetry project + tool config
└── .env.example         # environment variable template
```

---

## Requirements

| Tool | Version |
|------|---------|
| Python | ≥ 3.11 |
| Poetry | ≥ 1.8 |
| Docker + Docker Compose | ≥ 24 / v2 |

---

## Getting started

### 1. Clone and configure

```bash
git clone <repo-url> home-prefect
cd home-prefect
cp .env.example .env          # edit passwords / API URLs as needed
```

### 2. Install dependencies

Choose the group(s) that match your machine:

| Environment | Command |
|-------------|---------|
| Local dev (all groups) | `poetry install --with dev,server,worker` |
| Server only | `poetry install --with server` |
| Generic worker | `poetry install --with worker` |
| Raspberry Pi | `poetry install --with rpi` |

### 3. Start the Prefect stack with Docker

```bash
# Starts postgres + prefect-server (with UI) + worker
./scripts/start-stack.sh -d

# Open the Prefect UI
open http://localhost:4200
```

### 4. Create a work pool (first time only)

```bash
./scripts/create-work-pool.sh
```

### 5. Deploy flows

```bash
./scripts/deploy-flows.sh
```

---

## Development (Windows via Dev Container)

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and enable WSL2.
2. Install the VS Code **Dev Containers** extension.
3. Open this folder in VS Code → **F1 → Dev Containers: Reopen in Container**.
4. VS Code attaches to the devcontainer; the Prefect stack starts automatically.
5. Prefect UI is forwarded to `http://localhost:4200`.

---

## Dependency groups explained

| Group | Where | Purpose |
|-------|-------|---------|
| *(main)* | everywhere | `prefect`, `pydantic`, `httpx`, … |
| `server` | home server | PostgreSQL driver, `uvicorn` extras |
| `worker` | generic workers | flow-specific libraries (extend as needed) |
| `rpi` | Raspberry Pi | `gpiozero`, `smbus2` |
| `dev` | developer machine | `pytest`, `ruff`, `mypy`, `pre-commit` |

---

## Running tests

```bash
poetry run pytest
```

---

## Adding new flows

1. Create a new file in `src/home_prefect/flows/`.
2. Add tasks in `src/home_prefect/tasks/` if they are reusable.
3. Register a deployment in `src/home_prefect/deployments/`.
4. Run `./scripts/deploy-flows.sh` to push the deployment to the server.

---

## Useful commands

```bash
# Tail server logs
docker compose -f docker/docker-compose.yml logs -f prefect-server

# Enter the worker container
docker compose -f docker/docker-compose.yml exec prefect-worker bash

# Run a flow locally (no server required)
PYTHONPATH=src python src/home_prefect/flows/network_health.py

# Format & lint
poetry run ruff format .
poetry run ruff check . --fix
poetry run mypy src/
```

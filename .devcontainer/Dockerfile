# ─────────────────────────────────────────────────────────────────────────────
# .devcontainer/Dockerfile
#
# Development container: Python 3.11 + Poetry + common CLI tools.
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

ARG POETRY_VERSION=1.8.*

# System utilities
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      git curl wget iputils-ping jq bash-completion \
      # Docker CLI (so you can run `docker` inside the container)
      ca-certificates gnupg lsb-release \
 && install -m 0755 -d /etc/apt/keyrings \
 && curl -fsSL https://download.docker.com/linux/debian/gpg \
      | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
 && echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
      https://download.docker.com/linux/debian $(lsb_release -cs) stable" \
      > /etc/apt/sources.list.d/docker.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends docker-ce-cli docker-compose-plugin \
 && rm -rf /var/lib/apt/lists/*

# Poetry
RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

# Disable Poetry's virtual environment creation inside the container
# (the container itself IS the isolated environment)
RUN poetry config virtualenvs.create false

WORKDIR /workspaces/home-prefect

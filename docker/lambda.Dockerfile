# syntax=docker/dockerfile:1
ARG IMAGE

# hadolint ignore=DL3006
FROM ${IMAGE}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
WORKDIR /workspace

RUN pip install uv

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.lock,target=requirements.lock \
    pip wheel --wheel-dir /tmp/wheelhouse  --requirement <(sed '/^-e/d' requirements.lock)

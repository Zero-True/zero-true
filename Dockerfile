FROM debian:11-slim AS build
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes python3-venv gcc libpython3-dev && \
    python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip setuptools wheel

FROM build AS build-venv
# Set the working directory in the container
WORKDIR /usr/src/app

# Copy only the necessary dependency files first to leverage Docker cache
COPY . /usr/src/app

RUN /venv/bin/pip install --disable-pip-version-check .

# Install dependencies in a single layer to reduce image size
# RUN pip install --no-cache-dir .

# Install additional packages
RUN /venv/bin/pip install --no-cache-dir 'nodejs-bin[cmd]'

FROM gcr.io/distroless/python3-debian11
# FROM python:3.9.19-slim-bookworm

COPY --from=build-venv /venv /venv
COPY --from=build-venv /usr/local /usr/local
COPY . /app
WORKDIR /app
# Run zero-true app when the container launches
# EXPOSE 1326
ENTRYPOINT ["/venv/bin/python3", "/usr/local/bin/zero-true", "notebook", "0.0.0.0"]

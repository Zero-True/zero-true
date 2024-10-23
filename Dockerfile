# Use an official Python runtime as a parent image
ARG PYTHON_VERSION=3.9
FROM python:${PYTHON_VERSION}-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Set the working directory in the container
WORKDIR /app

# Create a virtual environment
RUN python -m venv /venv

# Copy the current directory contents into the container at /app
COPY . .

# Install packages specified in setup.py and nodejs-bin
RUN /venv/bin/pip install . && \
    /venv/bin/pip install 'nodejs-bin[cmd]'

# Remove the source files to keep the container clean
RUN rm -rf /app/*

# Create a non-root user
RUN mkdir /appuser && \
    groupadd -r -g 1001 appuser && \
    useradd -r -u 1001 -g appuser -d /appuser appuser && \
    chown -R appuser:appuser /app /appuser /venv

USER appuser

ENV PATH="/venv/bin:$PATH"

# Expose port and run zero-true app when the container launches
EXPOSE 1326
CMD ["zero-true", "notebook", "--host=0.0.0.0", "--remote"]

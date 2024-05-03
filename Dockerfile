# Use an official Python runtime as a parent image
FROM python:3.9.19-slim-bookworm as builder

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy only the necessary dependency files first to leverage Docker cache
COPY setup.py .

# Install dependencies in a single layer to reduce image size
RUN pip install --no-cache-dir .

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install additional packages
RUN pip install --no-cache-dir 'nodejs-bin[cmd]'

FROM gcr.io/distroless/python3

# Copy only the built artifacts and necessary scripts or configs from the builder stage
COPY --from=builder /usr/local /usr/local

# Run zero-true app when the container launches
EXPOSE 1326
CMD ["zero-true", "notebook", "0.0.0.0"]

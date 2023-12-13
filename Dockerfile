# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . /usr/src/app

# Install any needed packages specified in setup.py
RUN pip install . 

# Remove the source files to keep the container clean
RUN rm -rf /usr/src/app

# Run zero-true app when the container launches
CMD ["zero-true", "app"]

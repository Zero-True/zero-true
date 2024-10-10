# Use an official Python runtime as a parent image
ARG PYTHON_VERSION=3.9
FROM python:${PYTHON_VERSION}-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . /usr/src/app

# Install any needed packages specified in setup.py
RUN pip install . 
RUN pip install 'nodejs-bin[cmd]'

# Remove the source files to keep the container clean
RUN rm -rf /usr/src/app

# Run zero-true app when the container launches
EXPOSE 1326
CMD ["zero-true", "notebook", "--host=0.0.0.0", "--remote"]

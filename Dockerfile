# # Use an official Python runtime as the base image
# FROM python:3.9-slim

# # Set the working directory in the container
# WORKDIR /app

# # Copy the current directory contents into the container at /app
# COPY . /app

# # Upgrade pip
# RUN pip install --upgrade pip

# # Install any needed packages specified in requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# # Create a directory for the socket with appropriate permissions
# RUN mkdir -p /run/gunicorn && chmod 777 /run/gunicorn

# # Make port 8090 available to the world outside this container
# EXPOSE 8090

# # Define environment variable
# ENV FLASK_APP=main.py

# # Run app.py when the container launches
# CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "unix:/run/gunicorn/gunicorn.sock", "--max-requests", "1000", "--timeout", "300", "--limit-request-fields", "32768", "--limit-request-field_size", "0", "main:app"]

# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Upgrade pip
RUN pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create a directory for the socket with appropriate permissions
RUN mkdir -p /run/gunicorn && chmod 777 /run/gunicorn

# Make port 8090 available to the world outside this container
EXPOSE 8090

# Define environment variable
ENV FLASK_APP=main.py

# Run gunicorn when the container launches
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "unix:/run/gunicorn/gunicorn.sock", "--max-requests", "1000", "--timeout", "300", "--limit-request-line", "0", "--limit-request-fields", "32768", "--limit-request-field_size", "0", "main:app"]

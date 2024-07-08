# Use Python 3.9 slim image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Make port 8090 available to the world outside this container
EXPOSE 8090

# Define environment variable
ENV FLASK_APP=main.py

# Run gunicorn with gevent worker
CMD ["gunicorn", "--worker-class", "gevent", "--bind", "0.0.0.0:8090", "main:app"]
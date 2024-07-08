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

# Define environment variables
ENV FLASK_APP=main.py
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

# Run Flask development server instead of gunicorn for debugging
CMD ["flask", "run", "--host=0.0.0.0", "--port=8090"]
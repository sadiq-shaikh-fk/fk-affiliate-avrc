# Use Python 3.11 slim image
FROM python:3.11-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Make port 8090 available to the world outside this container
EXPOSE 8090

# Run gunicorn with eventlet worker
CMD ["gunicorn", "--worker-class", "eventlet", "--bind", "0.0.0.0:8090", "main:app"]
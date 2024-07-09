# Use Python 3.11 slim image
FROM python:3.11-slim-buster as builder

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application
COPY . .

# Create a new stage with a clean slim image
FROM python:3.11-slim-buster

# Copy only the necessary files from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app /app

# Set the working directory in the container
WORKDIR /app

# Make port 8090 available to the world outside this container
EXPOSE 8090

# Run gunicorn with eventlet worker
CMD ["gunicorn", "--worker-class", "eventlet", "--bind", "0.0.0.0:8090", "main:app"]
# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the image
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the image
COPY . .

# Expose the port the app runs on
EXPOSE 8090

# Run the application
CMD ["gunicorn", "-k", "gevent", "-b", "0.0.0.0:8080", "main:app"]
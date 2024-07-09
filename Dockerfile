# Use an official Python runtime as the base image
FROM python:3.9-slim

# Install Nginx
RUN apt-get update && apt-get install -y nginx

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Upgrade pip
RUN pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Make port 8090 available to the world outside this container
EXPOSE 8090

# Define environment variable
ENV FLASK_APP=main.py

# Start Nginx and Gunicorn
CMD service nginx start && gunicorn --worker-class eventlet -w 1 -b unix:/tmp/gunicorn.sock main:app
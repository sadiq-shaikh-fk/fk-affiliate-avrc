# Use the official Python image from the Docker Hub
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8090 available to the world outside this container
EXPOSE 8090

# Define environment variable
ENV FLASK_APP=main.py

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8090", "main:app"]
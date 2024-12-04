# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /webapp

# Install dependencies
COPY requirements.txt /webapp/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . /webapp/

# Expose port for the Flask application
EXPOSE 8085

# Define the environment variable for production
# ENV FLASK_ENV=prod

# Run the application
CMD ["python", "-m", "counter.entrypoints.webapp"]
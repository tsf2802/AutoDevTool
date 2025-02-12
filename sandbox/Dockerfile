# Start with a base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set an environment variable
ENV TEST_VAR="Hello from Dockerfile!"

# Copy our script into the container
COPY DFsandbox.py .

# Expose the port our app runs on
EXPOSE 8000

# Command to run when container starts
CMD ["python", "DFsandbox.py"] 
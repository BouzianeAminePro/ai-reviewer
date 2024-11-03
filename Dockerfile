# Use a Python base image
FROM python:3.11

# Install git
RUN apt-get update && apt-get install -y git

# Set the working directory
WORKDIR /app

# Copy the Python script into the container
COPY main.py .

# Set the command to run the Python script
ENTRYPOINT ["python", "/app/main.py"]

# Use an official Python runtime as a parent image
FROM python:3.9.18-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create a non-root user and switch to it
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Run main.py when the container launches
CMD ["python", "main.py"]

# Add healthcheck
HEALTHCHECK CMD python /app/healthcheck.py
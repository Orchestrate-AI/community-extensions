# Use an official Python runtime as the base image
FROM python:3.11-slim

# Install git and other necessary packages
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

ENV PYTHONUNBUFFERED=1

# Run main.py when the container launches
CMD ["python", "main.py"]
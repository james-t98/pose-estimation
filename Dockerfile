# Use the official Ubuntu 22.04 base image
FROM ubuntu:22.04

# Set environment variables for non-interactive apt commands and Python output
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install Python 3.10 and pip, along with all necessary system packages for OpenCV,
# Matplotlib, and other common scientific libraries.
# libgl1-mesa-glx, libxrender1, libsm6, libxext6 are crucial for OpenCV.
# libfontconfig1, libfreetype6-dev, libpng-dev are often needed for Matplotlib.
# build-essential and pkg-config are for building certain Python packages.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3.10 \
    python3-pip \
    python3.10-distutils \
    libgl1-mesa-glx \
    libxrender1 \
    libsm6 \
    libxext6 \
    libfontconfig1 \
    libfreetype6-dev \
    libpng-dev \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set python3.10 as the default python for consistency
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1 \
    && update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# Create a working directory inside the container
WORKDIR /app

# Copy the requirements file into the working directory
COPY requirements.txt .

# Install Python dependencies. Using --no-cache-dir helps keep the image size down.
# The system dependencies installed above should resolve the libGL.so.1 error.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the working directory
COPY . .

# Cloud Run services must listen on the port defined by the PORT environment variable.
# We set a default of 8080 if not provided by the environment.
ENV PORT 8080
EXPOSE $PORT

# Command to run your application.
# It's important to use 'python3.10' explicitly to ensure the correct interpreter is used.
# Flask's development server (app.run) binds to 0.0.0.0 by default when host is not specified,
# which is required for Cloud Run.
CMD ["python3.10", "main.py"]
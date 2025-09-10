# ========================================
# Base Image
# ========================================
FROM pytorch/pytorch:2.7.0-cuda12.8-cudnn9-runtime

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# ========================================
# System Dependencies
# ========================================
RUN apt-get update && apt-get install -y \
    ca-certificates \
    python3 python3-pip python3-venv \
    git build-essential curl ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Ensure CA certificates are up-to-date
RUN update-ca-certificates

# ========================================
# Custom SSL Certificate
# ========================================
COPY AMP_XGS2100_Sophos.crt /usr/local/share/ca-certificates/AMP_XGS2100_Sophos.crt
RUN update-ca-certificates

# Set environment variables so Python and requests trust updated CA bundle-
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

# ========================================
# Python Configuration
# ========================================
# Make 'python' alias point to 'python3'
RUN ln -s /usr/bin/python3 /usr/bin/python

# Upgrade pip and configure to use trusted CA
RUN pip install --upgrade pip && \
    pip config set global.cert /etc/ssl/certs/ca-certificates.crt

# Install pip and setuptools with trusted hosts
RUN pip install \
    --trusted-host pypi.org \
    --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org \
    pip setuptools

# ========================================
# Application Setup
# ========================================
WORKDIR /app

# Copy dependency list first for better layer caching

COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application files
COPY . .
# RUN pip install pyarmor
# COPY ./noise_percent_poc.py .
# ========================================
# Port & Entrypoint
# ========================================
EXPOSE 7860
CMD ["python3", "app.py"]
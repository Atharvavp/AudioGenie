# Use an official PyTorch image with CUDA 12.8
# Look for the latest stable version tag with cuda12.8 on Docker Hub:
# https://hub.docker.com/r/pytorch/pytorch/tags/
# As of the last update, a tag like 2.7.0-cuda12.8-cudnn*-runtime should be available.

FROM pytorch/pytorch:2.7.0-cuda12.8-cudnn9-devel

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies including CA cert utilities
RUN apt-get update && apt-get install -y \
    ca-certificates \
    python3 python3-pip python3-venv git build-essential curl ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Ensure ca-certificates is up to date
RUN update-ca-certificates

# Copy custom certificate and rename to .crt (required for update-ca-certificates)
COPY /AMP_XGS2100_Sophos.crt /usr/local/share/ca-certificates/AMP_XGS2100_Sophos.crt

# Update CA cert store with the new custom certificate
RUN update-ca-certificates

# Set environment variables so Python trusts the updated CA bundle
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

# Make 'python' point to 'python3'
RUN ln -s /usr/bin/python3 /usr/bin/python

# Upgrade pip and configure to use trusted CA
RUN pip install --upgrade pip && \
    pip config set global.cert /etc/ssl/certs/ca-certificates.crt

# Install pip and setuptools with trusted hosts
RUN pip install --trusted-host pypi.org \
                --trusted-host pypi.python.org \
                --trusted-host files.pythonhosted.org \
                pip setuptools

WORKDIR /app 

ADD requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

RUN pip install streamlit

EXPOSE 8501 8501

CMD ["sleep", "infinity"]



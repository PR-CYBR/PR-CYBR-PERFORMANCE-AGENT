# syntax=docker/dockerfile:1

FROM python:3.11-slim as base

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app

# Install OS dependencies required for performance monitoring and diagnostics
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        iputils-ping \
        netcat-openbsd \
        net-tools \
        procps \
        tini \
    && rm -rf /var/lib/apt/lists/*

# Create application directory and non-root user
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR ${APP_HOME}

# Install Python dependencies first to leverage Docker layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && if [ -s requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy application source
COPY . ${APP_HOME}

# Ensure runtime directories exist for mounted volumes used by monitoring workflows
RUN mkdir -p ${APP_HOME}/logs ${APP_HOME}/data \
    && chown -R appuser:appuser ${APP_HOME}

# Expose ports for the dashboard (HTTP) and metrics endpoints
EXPOSE 80 9090

# Switch to the non-root user for security
USER appuser

ENTRYPOINT ["tini", "--"]
CMD ["python", "src/main.py"]

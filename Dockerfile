# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies for native packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    python3-dev \
    linux-libc-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Raspberry Pi specific dependencies (optional, for hardware mode)
RUN pip install --no-cache-dir adafruit-circuitpython-dht RPi.GPIO || true


# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies for GPIO access
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgpiod-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY app.py .

# Environment variables
ENV MOCK_SENSORS=True
ENV DHT_PIN=4
ENV PORT=5000

EXPOSE 5000

# Run as non-root user (except when using GPIO)
RUN useradd -m -u 1000 appuser
USER appuser

CMD ["python", "app.py"]

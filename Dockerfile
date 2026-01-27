FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "run.py"]
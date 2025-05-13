#############################################################
# 1. BUILD STAGE – install deps                             #
#############################################################
FROM python:3.12-slim AS builder
WORKDIR /app

# Install OS libs needed by matplotlib, torch et al.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libopenblas-dev liblapack-dev libomp-dev \
    libfreetype6-dev libpng-dev libmagic1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

# If you pin torch, add the extra-index URL for CPU wheels
# (remove if requirements.txt already contains torch==..+cpu )
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
#############################################################
# 2. RUNTIME STAGE – slim image with deps + code            #
#############################################################
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY --from=builder /usr/local/lib/python3.12/site-packages \
    /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
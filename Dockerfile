FROM python:3.13

WORKDIR /app

# Install netcat for entrypoint health checks
RUN apt-get update \
    && apt-get install -y --no-install-recommends netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Ensure entrypoint script is executable
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

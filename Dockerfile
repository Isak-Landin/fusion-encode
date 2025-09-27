FROM python:3.12-slim

# System deps (optional but nice to have)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install deps first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Default envs
ENV PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

# Expose the Flask app port (matches APP_PORT)
EXPOSE 5009

# Run with gunicorn for production
# If your app module is app.py with variable "app"
CMD ["gunicorn", "--bind", "0.0.0.0:5009", "--workers", "2", "app:app"]

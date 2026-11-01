# Production image for the Jahan art shop (Django + gunicorn)
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 curl gettext \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Prepare entrypoint and permissions
RUN sed -i 's/\r$//' /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh \
    && useradd -m app \
    && mkdir -p /app/media /app/staticfiles \
    && chown -R app:app /app

USER app

# Compile Django translations
RUN python manage.py compilemessages

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
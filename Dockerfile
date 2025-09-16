# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Run migrations (will be overridden by Railway)
RUN python manage.py migrate --run-syncdb

# Expose port
EXPOSE $PORT

# Run gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn tvservices.wsgi:application --bind 0.0.0.0:$PORT"]

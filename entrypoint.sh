#!/bin/sh

# Run Alembic migrations
alembic upgrade head

# Start Celery in the background
su -c 'celery -A app.celery.celery worker --beat --loglevel=info --logfile=celery.log &' appuser

# Start Uvicorn server
exec "$@"
from celery import Celery
import requests

from app.core.constants import BASE_URL, API_KEY, REDIS_URL

# Create a Celery app
celery_app = Celery('tasks', broker=REDIS_URL)  

# Defining the task that will call the endpoint
@celery_app.task
def finalize_challenges():
    try:
        headers = {
            'X-API-Key': API_KEY,
            'Content-Type': 'application/json'
        }
        response = requests.post(url=BASE_URL, headers=headers)
        response.raise_for_status()  # Check for successful response
        print("Challenges finalized successfully")
    except requests.exceptions.RequestException as e:
        print(f"Error finalizing challenges: {e}")

# Schedule the task to run every 30 minutes
celery_app.conf.beat_schedule = {
    'finalize-challenges-every-30-minutes': {
        'task': 'tasks.finalize_challenges',
        'schedule': 30 * 60,  # 30 minutes in seconds
    },
}


from celery import Celery
import os

REDIS_URL = os.environ.get("REDISCLOUD_URL", 'redis://localhost:6379/0')

def make_celery(app):
    # Initialize the Celery object with the Flask app's name and broker (Redis in this case)
    celery = Celery(app.import_name,
                    broker='redis://localhost:6379/0',
                    backend='redis://localhost:6379/0')
    
    # Bind the Flask app's context to Celery
    celery.conf.update(app.config)
    
    return celery

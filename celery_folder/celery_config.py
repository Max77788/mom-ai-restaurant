from celery import Celery
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

REDIS_URL = os.environ.get("REDIS_URL", 'redis://localhost:6379/0')

# REDIS_URL = "redis://default:o2KYAAZF8HJeK0IlTf6wtsz14mdxXJTD@redis-11649.c85.us-east-1-2.ec2.redns.redis-cloud.com:11649"

def make_celery(app):
    # Initialize the Celery object with the Flask app's name and broker (Redis in this case)
    celery = Celery(app.import_name,
                    broker=REDIS_URL,
                    backend=REDIS_URL)
    
    # Bind the Flask app's context to Celery
    celery.conf.update(app.config)
    
    return celery

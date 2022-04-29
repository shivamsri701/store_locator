import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storelocator.settings')

app = Celery('storelocator', broker="redis://localhost:6379")

BASE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.broker_url = BASE_REDIS_URL


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
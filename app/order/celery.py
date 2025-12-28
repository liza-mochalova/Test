import time

from celery import Celery
from fastapi import FastAPI


@shared_task()
def call_background_task.apply_async(args=[arg1_value], kwargs={'key': 'value'}):
    time.sleep(10)
    print(f"Background Task called!")
    print(message)
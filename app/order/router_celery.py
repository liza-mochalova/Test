from celery import Celery

app = Celery(
    'tasks',
    broker='redis://localhost:6379/0', 
)

@app.task(queue='high_priority')
def high_priority_task():
    print("Выполнение задачи высокого приоритета")

@app.task(queue='normal_priority')
def normal_priority_task():
    print("Выполнение задачи среднего приоритета")

@app.task(queue='low_priority')
def low_priority_task():
    print("Выполнение задачи низкого приоритета")

from datetime import datetime, timedelta
import operator

from scheduler import Scheduler
from task import Task


y = Task(None, print, (22, 22), start_at=datetime.now() + timedelta(seconds=3))
t = Task(None, print, (900, 100), start_at=datetime.now() + timedelta(seconds=1), dependencies=[y])
tasks = [
    Task(None, print, (44, 44), start_at=datetime.now() + timedelta(seconds=4)),
    Task(None, print, (11, 11)),
    Task(None, print, (333, 333), start_at=datetime.now() + timedelta(seconds=2), dependencies=[t]),
    Task(None, operator.truediv, (10, 0), attempts=3),
]

scheduler = Scheduler()

[scheduler.schedule(task) for task in tasks]
scheduler.stop()


scheduler = Scheduler()
scheduler.load()

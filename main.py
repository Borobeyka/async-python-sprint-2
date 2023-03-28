from datetime import datetime, timedelta

from scheduler import Scheduler
from task import Task

# import operator


subtask1 = Task(None, print, (22, 22))
subtask2 = Task(None, print, (900, 100), dependencies=[subtask1])
tasks = [
    Task(None, print, (44, 44), dependencies=[subtask2], start_at=datetime.now() + timedelta(seconds=1)),
    Task(None, print, (10, 0)),
    Task(None, print, (100, 100), attempts=2),
]

scheduler = Scheduler(0)

[scheduler.schedule(task) for task in tasks]
scheduler.run()

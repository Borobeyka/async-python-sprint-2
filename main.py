from datetime import datetime, timedelta

from logger import logger
from scheduler import Scheduler
from task import Task, Status

import operator

# tasks2 = [item for item in list if item % 2 == 0][:10:]


# y = Task( None, print, (22, 22), start_at=datetime.now() + timedelta(seconds=3) )
# t = Task( None, print, (900, 100), start_at=datetime.now() + timedelta(seconds=1), dependencies=[y] )
tasks = [
    Task( None, print, (11, 11), start_at=datetime.now() + timedelta(seconds=3) ),
    Task( None, print, (333, 333), start_at=datetime.now() + timedelta(seconds=2) ),
    Task( None, operator.truediv, (10, 0), attempts=2),
]

scheduler = Scheduler()

[scheduler.schedule(task) for task in tasks]
scheduler.run()
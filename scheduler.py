from threading import Timer
from typing import List, Callable, Generator
from datetime import datetime, timedelta
from functools import wraps
from time import sleep

# from uuid import uuid4

from logger import logger
from task import Task, Status

"""
    • Нужно ли удалять задачи из планировщика после завершения?
"""

def coroutine(func: Callable) -> Callable:
    @wraps(func)
    def wrap(*args, **kwargs) -> Generator:
        gen = func(*args, **kwargs)
        next(gen)
        return gen
    return wrap

class Scheduler:
    def __init__(self, pool_size: int = 10):
        self.pool_size = pool_size
        self.tasks: List[Task] = []
        self.attempts_interval = timedelta(seconds=4)
        self.is_run = True


    def schedule(self, task: Task) -> None:
        if self.is_task_exists(task):
            logger.debug(f"{task.prefix} has already added")
            return

        for subtask in task.dependencies:
            if not self.is_task_exists(subtask):
                self.schedule(subtask)
                task.start_at = subtask.start_at + timedelta(seconds=.1)

        self.tasks.append(task)
        logger.debug(f"{task.prefix} was added with {len(task.dependencies)} dependencies")

    @coroutine
    def start_task(self) -> None:
        while True:
            task = (yield)
            try:
                task.run()
            except Exception:
                task.attempts -= 1
                if task.attempts > 0:
                    task.status = Status.IN_QUEUE
                    task.start_at += self.attempts_interval
                else:
                    task.status = Status.ERROR
                logger.debug(f"{task.prefix} fault with error ({task.attempts} attempts left)")

                
    def run(self):
        executor = self.start_task()
        while self.is_run and self.tasks_count():
            for task in self.get_tasks():
                task.status = Status.IN_PROGRESS
                executor.send(task)
            
    def get_tasks(self):
        self.sort()
        # task = self.tasks.pop(0)
        # yield self.tasks[0]
        for task in [ task for task in self.tasks if task.status == Status.IN_QUEUE ][:self.pool_size]:
            yield task

        
    def sort(self) -> None:
        self.tasks = sorted(self.tasks, key=lambda x: x.status == Status.IN_QUEUE, reverse=True)

    def is_task_exists(self, task: Task) -> bool:
        return task in self.tasks
    
    def tasks_count(self) -> int:
        return len([task for task in self.tasks if task.status not in [Status.ERROR, Status.COMPLETED]])

    def restart(self):
        return NotImplemented

    def stop(self):
        self.is_run = False


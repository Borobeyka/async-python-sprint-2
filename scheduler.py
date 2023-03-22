from typing import List, Callable, Generator
from datetime import timedelta
from functools import wraps
import pickle

from singleton import Singleton
from logger import logger
from task import Task, Status

BACKUP_FILENAME = "backup.pkl"
ATTEMPTS_INTERVAL = timedelta(seconds=4)

"""
    • Нужно ли удалять задачи из планировщика после завершения?
    • (Если "нет") Нужно ли сохранять в бэкап выполненные или выполненные с ошибкой задачи?
"""


def coroutine(func: Callable) -> Callable:
    @wraps(func)
    def wrap(*args, **kwargs) -> Generator:
        gen = func(*args, **kwargs)
        next(gen)
        return gen
    return wrap


class Scheduler(metaclass=Singleton):
    def __init__(self, pool_size: int = 10):
        self.pool_size = pool_size
        self.tasks: List[Task] = []
        self.attempts_interval = ATTEMPTS_INTERVAL

    def schedule(self, task: Task) -> None:
        if self.is_task_exists(task):
            logger.debug(f"{task.prefix} has already added")
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
            except Exception as ex:
                task.attempts -= 1
                if task.attempts > 0:
                    task.status = Status.IN_QUEUE
                    task.start_at += self.attempts_interval
                else:
                    task.status = Status.ERROR
                logger.debug(f"{task.prefix} fault with error ({task.attempts} attempts left) (Error: {ex})")

    def run(self) -> None:
        self.is_run = True
        executor = self.start_task()
        while self.is_run and self.tasks_count():
            for task in self.get_tasks():
                task.status = Status.IN_PROGRESS
                executor.send(task)

    def get_tasks(self) -> Generator[Task, None, None]:
        self.sort()
        for task in [task for task in self.tasks if task.status == Status.IN_QUEUE][:self.pool_size]:
            yield task

    def sort(self) -> None:
        self.tasks = sorted(
            self.tasks,
            key=lambda x: x.status == Status.IN_QUEUE,
            reverse=True
        )

    def is_task_exists(self, task: Task) -> bool:
        return task in self.tasks

    def tasks_count(self) -> int:
        return len([
            task for task in self.tasks
            if task.status not in [Status.ERROR, Status.COMPLETED]
        ])

    def stop(self) -> None:
        self.is_run = False
        with open(BACKUP_FILENAME, "wb") as file:
            pickle.dump(self.tasks, file, pickle.HIGHEST_PROTOCOL)
        logger.debug("Scheduler stopped, tasks saved")

    def load(self) -> None:
        try:
            with open(BACKUP_FILENAME, "rb") as f:
                self.tasks = pickle.load(f)
        except FileNotFoundError:
            logger.debug("Couldnt open file, check path file")
        else:
            logger.debug("Scheduler loaded, tasks restored")
            self.run()

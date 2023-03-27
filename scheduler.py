from typing import List, Callable, Generator
from functools import wraps
import pickle

from singleton import Singleton
from logger import logger
from task import Task, Status, EarlyExecutionTask

from settings import Settings


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
        self.attempts_interval = Settings.ATTEMPTS_INTERVAL

    def schedule(self, task: Task) -> None:
        if self.is_task_exists(task):
            logger.debug(f"{task.prefix} has already added")
            return
        self.tasks.append(task)
        logger.debug(f"{task.prefix} was added with {len(task.dependencies)} dependencies")

    def run(self) -> None:
        self.is_run = True
        while self.is_run and self.tasks_count():
            task = self.get_task()
            if not task:
                continue
            try:
                task_gen = task.run()
                next(task_gen)

                # Правильно ли здесь пишу - next(task_gen)
                # Что бы тут не писал, код не выполняется, почему?

            except StopIteration:
                task.status = Status.COMPLETED
                continue
            except EarlyExecutionTask:
                task.status = Status.WAITING
                self.schedule(task)
                continue
            except Exception as ex:
                task.status = Status.ERROR
                logger.debug(f"{task.prefix} fault with error ({ex})")
                # ! TRIES ADD HERE
                continue
            task.status = Status.IN_QUEUE
            self.schedule(task)

    def get_task(self) -> Task | bool:
        self.sort()
        if self.tasks[0].status != Status.IN_QUEUE:
            return False
        task = self.tasks.pop(0)
        task.status = Status.IN_PROGRESS
        return task

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
        with open(Settings.BACKUP_FILENAME, "wb") as file:
            pickle.dump(self.tasks, file, pickle.HIGHEST_PROTOCOL)
        logger.debug("Scheduler stopped, tasks saved")

    def load(self) -> None:
        try:
            with open(Settings.BACKUP_FILENAME, "rb") as f:
                self.tasks = pickle.load(f)
        except FileNotFoundError:
            logger.debug("Couldnt open file, check path file")
        else:
            logger.debug("Scheduler loaded, tasks restored")

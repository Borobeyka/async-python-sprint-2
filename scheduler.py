from datetime import datetime
from typing import List

import pickle

from singleton import Singleton
from task import Task, Status
from logger import logger
from settings import Settings
from exceptions import (
    EarlyExecutionTask,
    DependenciesNotReady,
    ExecutionTimeoutOut
)


class Scheduler(metaclass=Singleton):
    def __init__(self, max_pool_size: int = 10):
        self.max_pool_size = max_pool_size
        self.cur_pool_size = 0
        self.tasks: List[Task] = []
        self.attempts_interval = Settings.ATTEMPTS_INTERVAL

    def schedule(self, task: Task) -> None:
        if self.is_task_exists(task):
            logger.debug(f"{task.prefix} has already added")
            return
        task.status = Status.IN_QUEUE
        self.tasks.append(task)

    def run(self) -> None:
        self.is_run = True
        while self.is_run and self.tasks_count():
            if self.cur_pool_size >= self.max_pool_size:
                continue
            try:
                task = self.get_task()
                if not task:
                    break
                self.cur_pool_size += 1
                if task.generator is None:
                    if not task.is_able_to_run():
                        raise EarlyExecutionTask
                    logger.debug(f"{task.prefix} is running")
                    task.generator = task.run()
                next(task.generator)
                if not task.is_dependencies_completed():
                    raise DependenciesNotReady
                if (datetime.now() - task.started_at).total_seconds() > task.timeout:
                    raise ExecutionTimeoutOut
                self.schedule(task)
            except StopIteration:
                logger.debug(f"{task.prefix} completed (with {len(task.dependencies)} dependencies)")
                task.status = Status.COMPLETED
            except EarlyExecutionTask:
                self.schedule(task)
            except DependenciesNotReady:
                logger.debug(f"{task.prefix} not all dependencies done")
                self.schedule(task)
            except (ExecutionTimeoutOut, Exception) as ex:
                if type(ex) == ExecutionTimeoutOut:
                    logger.debug(f"{task.prefix} execution timeout out")
                if task.attempts > 0:
                    task.attempts -= 1
                    task.start_at = datetime.now() + Settings.ATTEMPTS_INTERVAL
                    self.schedule(task)
                logger.debug(f"{task.prefix} fault with error, attempts left {task.attempts} (Error: {ex})")
            finally:
                self.cur_pool_size -= 1
        logger.debug("All tasks completed")

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

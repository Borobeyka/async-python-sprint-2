from typing import List, Dict, Callable
from datetime import datetime, timedelta
from threading import Timer
from enum import Enum
from time import sleep

from uuid import uuid4

from logger import logger

class Status(Enum):
    IN_QUEUE = 1,
    IN_PROGRESS = 2,
    COMPLETED = 3,
    ERROR = 4,

class Task:
    def __init__(
            self,
            id: uuid4,
            func: Callable,
            args: List = [],
            kwargs: Dict = {},
            start_at: datetime = datetime.now(),
            max_working_time: int = -1,
            attempts: int = 0,
            dependencies: List = [],
            status: Status = Status.IN_QUEUE
        ):
        self.id = id if id is not None else uuid4()
        self.func = func
        self.name = func.__name__
        self.args = args
        self.kwargs = kwargs
        self.start_at = start_at
        self.max_working_time = max_working_time
        self.attempts = attempts
        self.dependencies = dependencies
        self.status = status
        self.prefix = f"Task \"{self.name}\" [ID: {self.id}]"

    def run(self):
        now = datetime.now()
        if (difference_time := (self.start_at - now).total_seconds()) > 0:
            logger.debug(f"{self.prefix} waiting for run at {self.start_at}")
            #! Ну как запустить через время
            Timer(difference_time, self.run).start()
            # sleep(difference_time)
        else:
            logger.debug(f"{self.prefix} is running")
            self.func(*self.args, **self.kwargs)
            logger.debug(f"{self.prefix} completed")
            self.status = Status.COMPLETED

    def pause(self):
        pass

    def stop(self):
        pass
from typing import List, Dict, Callable
from datetime import datetime
from threading import Timer
from enum import Enum

from uuid import uuid4

from logger import logger


class Status(Enum):
    IN_QUEUE = 1
    IN_PROGRESS = 2
    WAITING = 3
    COMPLETED = 4
    ERROR = 5


class Task:
    def __init__(
            self,
            ident: uuid4,
            func: Callable,
            args: List = None,
            kwargs: Dict = None,
            start_at: datetime = datetime.now(),
            attempts: int = 0,
            dependencies: List = [],
            status: Status = Status.IN_QUEUE
    ):
        self.ident = ident if ident is not None else uuid4()
        self.func = func
        self.name = func.__name__
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.start_at = start_at
        self.attempts = attempts
        self.dependencies = dependencies
        self.status = status
        self.prefix = f"Task \"{self.name}\" [ID: {self.ident}]"

    def run(self):
        now = datetime.now()
        if (difference_time := (self.start_at - now).total_seconds()) > 0:
            logger.debug(f"{self.prefix} waiting for run at {self.start_at}")
            Timer(difference_time, self.reset).start()
            self.status = Status.WAITING
        else:
            logger.debug(f"{self.prefix} is running")
            try:
                self.func(*self.args, **self.kwargs)
            except Exception as ex:
                raise Exception(ex) from ex
            else:
                logger.debug(f"{self.prefix} completed")
                self.status = Status.COMPLETED

    def reset(self):
        self.status = Status.IN_QUEUE

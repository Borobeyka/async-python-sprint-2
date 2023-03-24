from __future__ import annotations
from typing import List, Dict, Callable, Optional
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
            ident: Optional[uuid4],
            func: Callable,
            args: Optional[List] = None,
            kwargs: Optional[Dict] = None,
            start_at: Optional[datetime] = None,
            attempts: Optional[int] = None,
            dependencies: Optional[List[Task]] = None,
            status: Status = Status.IN_QUEUE
    ):
        self.ident = ident or uuid4()
        self.func = func
        self.name = func.__name__
        self.args = args or []
        self.kwargs = kwargs or {}
        self.start_at = start_at or datetime.now()
        self.attempts = attempts or 0
        self.dependencies = dependencies or []
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

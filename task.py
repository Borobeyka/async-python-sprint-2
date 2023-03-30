from __future__ import annotations
from typing import List, Dict, Callable, Optional, Generator
from datetime import datetime
from enum import Enum

from uuid import uuid4

from settings import Settings


class Status(Enum):
    IN_QUEUE = 1
    IN_PROGRESS = 2
    COMPLETED = 3
    ERROR = 4


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
            timeout: Optional[int] = None,
            generator: Optional[Generator] = None,
            status: Status = Status.IN_QUEUE
    ):
        self.ident = ident or uuid4()
        self.func = func
        self.name = func.__name__
        self.args = args or []
        self.kwargs = kwargs or {}
        self.start_at = start_at or None
        self.attempts = attempts or 0
        self.dependencies = dependencies or []
        self.timeout = timeout or Settings.TIMEOUT_SECONDS
        self.status = status
        self.prefix = f"Task \"{self.name}\" [ID: {self.ident}]"
        self.generator = generator

    def run(self):
        for dependence in self.dependencies:
            yield from dependence.run()
        self.started_at = datetime.now()
        yield self.func(*self.args, **self.kwargs)

    def is_able_to_run(self) -> bool:
        if self.start_at is None or self.start_at <= datetime.now():
            return True
        return False

    def is_dependencies_completed(self) -> bool:
        for dependence in self.dependencies:
            if dependence.status != Status.COMPLETED:
                return False
        return True

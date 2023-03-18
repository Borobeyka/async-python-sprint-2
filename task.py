from typing import List, Dict, Callable
from datetime import datetime
from enum import Enum

from uuid import uuid4

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
        self.id = id
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.start_at = start_at
        self.max_working_time = max_working_time
        self.attempts = attempts
        self.dependencies = dependencies
        self.status = status

    def run(self):
        return self.func(*self.args, **self.kwargs)

    def pause(self):
        pass

    def stop(self):
        pass
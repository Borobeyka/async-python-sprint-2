from __future__ import annotations
from threading import Timer
from typing import List, Dict, Callable, Optional
from datetime import datetime
from enum import Enum

from uuid import uuid4

from settings import Settings
from logger import logger


class Status(Enum):
    IN_QUEUE = 1
    IN_PROGRESS = 2
    WAITING = 3
    COMPLETED = 4
    ERROR = 5


class EarlyExecutionTask(Exception):
    pass


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
        self.timeout = timeout or Settings.TIMEOUT_SECONDS
        self.status = status
        self.prefix = f"Task \"{self.name}\" [ID: {self.ident}]"

    def run(self):
        for dependence in self.dependencies:
            logger.debug(f"{self.prefix} started the dependence - {dependence.prefix}")
            yield from dependence.run()

        # Вопрос 1
        # Дочерние таски выполняются, все ок. Когда главная таска отложена - выкидываю кастомную ошибку
        # что ранний запуск. После когда наступает время выполнения - выполняются зависимости, хотя они
        # уже были ранее выполнены... Направьте, пожалуйста, как следует реализовывать.
        # Пересмотрел не один десяток раз материалы курса, но все равно не понимаю

        # Вопрос 2
        # Как можно реализовать таймаут на исполнение?
        # (Время до запуска - время после выполнения) и если больше таймаута, то ошибка?
        # Таким образом таска все равно ведь выполнится...

        if (difference_time := (self.start_at - datetime.now()).total_seconds()) > 0:
            logger.debug(f"{self.prefix} waiting for run at {self.start_at}")
            Timer(difference_time, self.reset).start()
            raise EarlyExecutionTask
        else:
            logger.debug(f"{self.prefix} is running")
            self.func(*self.args, **self.kwargs)
            logger.debug(f"{self.prefix} completed")

    def reset(self):
        self.status = Status.IN_QUEUE

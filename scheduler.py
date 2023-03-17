from typing import Callable, Generator

from job import Job

def caroutine(func: Callable) -> Callable:
    def wrap(*args, **kwargs) -> Generator:
        gen = func(*args, **kwargs)
        gen.send(None)
        return gen
    return wrap

class Scheduler:
    def __init__(self, pool_size: int = 10):
        self.queue = []
        self.pool_size = pool_size


    def schedule(self, task: Job):
        if len(self.queue) <= self.pool_size:
            self.queue.append(task)

    def run(self):
        pass

    def restart(self):
        pass

    def stop(self):
        pass

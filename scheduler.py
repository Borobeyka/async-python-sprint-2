from typing import List, Callable, Generator
from datetime import datettime, timedelta
from time import sleep


from task import Task, Status


class Scheduler:
    def __init__(self, pool_size: int = 10):
        self.pool_size = pool_size
        self.tasks: List[Task] = []
        self.attempts_interval = timedelta(seconds=30)

        self.is_run = True


    # def add(self, task: Job):
    #     self.tasks.append(task)

    def start_task(self) -> None:
        while True:
            task: Task = (yield)
            try:
                task.run()
                task.status = Status.COMPLETED
                #! ADD LOGGER "Task [ID] completed"
            except Exception as ex:
                if task.attempts > 0:
                    task.attempts -= 1
                    task.status = Status.IN_QUEUE
                    task.start_at += self.attempts_interval
                    #! ADD LOGGER "Task [ID] add to queue, x/n attempts left"
                else:
                    task.status = Status.ERROR
                    #! ADD LOGGER "Task [ID] fault with error (ex)"
                
    def extract_task(self):
        while self.is_run:
            self.sort()
            if (task := self.tasks.pop(0)).status == Status.IN_QUEUE:
                now = datettime.now()
                difference_time = (task.start_at - now).total_seconds()
                if difference_time > 0:
                    sleep(difference_time)
        
    def sort(self) -> None:
        self.tasks = sorted(self.tasks, key=lambda x: x == Status.IN_QUEUE, reverse=True)


    def run(self):
        return NotImplemented

    def restart(self):
        return NotImplemented

    def stop(self):
        self.is_run = False

def caroutine(func: Callable) -> Callable:
    def wrap(*args, **kwargs) -> Generator:
        gen = func(*args, **kwargs)
        gen.send(None)
        return gen
    return wrap
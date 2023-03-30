from datetime import datetime, timedelta
import operator
import os

from scheduler import Scheduler
from task import Task


def task1():
    os.makedirs("temp")


def task2():
    with open("temp/file_task_1.txt", "w", encoding="utf8") as file:
        file.write("Hello from task1")


def main():
    subtask3_1 = Task(None, print, (22, 22))
    tasks = [
        Task(None, task1, start_at=datetime.now() + timedelta(seconds=1)),
        Task(None, task2, start_at=datetime.now() + timedelta(seconds=2)),
        Task(None, print, (900, 100), dependencies=[subtask3_1]),
        Task(None, operator.truediv, (10, 0), attempts=3),
    ]

    scheduler = Scheduler()

    [scheduler.schedule(task) for task in tasks]

    scheduler.stop()
    scheduler.load()
    scheduler.run()


if __name__ == "__main__":
    main()

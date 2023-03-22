import unittest

from scheduler import Scheduler
from task import Task


class Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scheduler = Scheduler()
        print("Tests started")

    def test_execute_task(self):
        self.scheduler.schedule(Task(None, task, args=(1, 0)))
        self.scheduler.run()


def task(a: int, b: int):
    print(f"Division is {a / b}")


if __name__ == "__main__":
    unittest.main()

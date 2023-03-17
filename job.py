from datetime import datetime

class Job:
    def __init__(
            self,
            start_at: datetime = datetime.now(),
            max_working_time: int = -1,
            tries: int = 0,
            dependencies: list = []
        ):
        self.start_at = start_at
        self.max_working_time = max_working_time
        self.tries = tries
        self.dependencies = dependencies

    def run(self):
        pass

    def pause(self):
        pass

    def stop(self):
        pass

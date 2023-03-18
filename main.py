from functools import reduce

from scheduler import Scheduler
from task import Task, Status

l = [Status.IN_QUEUE, Status.COMPLETED, Status.IN_QUEUE, Status.COMPLETED, Status.IN_PROGRESS]
print(l)
sorted_list = sorted(l, key=lambda x: x == Status.IN_QUEUE, reverse=True)
# print(sorted_list)
# map(lambda x: print(x), sorted_list)
[print(x) for x in sorted_list]
# sorted()
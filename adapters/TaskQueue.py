from typing import Callable

from fastapi import BackgroundTasks


class TaskQueue:
    _background_tasks: BackgroundTasks

    def __init__(self, background_tasks: BackgroundTasks):
        self._background_tasks = background_tasks

    def __call__(self, task: Callable, *args, **kwargs):
       self._background_tasks.add_task(task, *args, **kwargs)

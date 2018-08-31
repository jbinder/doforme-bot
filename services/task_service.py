from datetime import datetime

from pony.orm import db_session, commit, select

from data.db import Task


class TaskService:
    @db_session
    def add_task(self, data):
        Task(
            user_id=data['user_id'],
            chat_id=data['chat_id'],
            owner_id=data['owner_id'],
            title=data['title'],
            created=datetime.utcnow(),
            due=data['due'])
        commit()

    @db_session
    def get_tasks(self, user_id):
        # noinspection PyTypeChecker
        return select(task for task in Task if task.user_id == user_id)[:]

    @db_session
    def complete_task(self, task_id):
        Task[task_id].done = datetime.utcnow()
        commit()

    @db_session
    def get_task(self, task_id):
        return Task[task_id]


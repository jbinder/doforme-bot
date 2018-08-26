from pony.orm import db_session, commit, select

from data.db import Task


class TaskService:
    @db_session
    def add_task(self, data):
        Task(user_id=data['user_id'], chat_id=data['chat_id'], owner_id=data['owner_id'], title=data['title'])
        commit()

    @db_session
    def get_tasks(self, user_id):
        # noinspection PyTypeChecker
        return select(task for task in Task if task.user_id == user_id)[:]

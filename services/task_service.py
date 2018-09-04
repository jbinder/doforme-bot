from datetime import datetime, timedelta

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
        return select(task for task in Task if task.user_id == user_id).order_by(lambda t: t.due)[:]

    @db_session
    def get_due_today(self, user_id):
        # noinspection PyTypeChecker
        return select(task for task in Task
                      if (task.user_id == user_id) and (task.done is None) and (task.due.date() == datetime.today().date())
                      ).order_by(lambda t: t.due)[:]

    @db_session
    def get_due_this_week(self, user_id):
        # noinspection PyTypeChecker
        return select(task for task in Task
                      if (task.user_id == user_id) and (task.done is None) and (task.due.date() > datetime.today().date()) and
                      (task.due.date() <= datetime.today() + timedelta(days=7))
                      ).order_by(lambda t: t.due)[:]

    @db_session
    def get_due_later_than_this_week(self, user_id):
        # noinspection PyTypeChecker
        return select(task for task in Task
                      if (task.user_id == user_id) and (task.done is None) and (task.due.date() > datetime.today().date() + timedelta(days=7))
                      ).order_by(lambda t: t.due)[:]

    @db_session
    def get_due_past(self, user_id):
        # noinspection PyTypeChecker
        return select(task for task in Task
                      if (task.user_id == user_id) and (task.done is None) and (task.due.date() < datetime.today().date())
                      ).order_by(lambda t: t.due)[:]

    @db_session
    def get_due_undefined(self, user_id):
        # noinspection PyTypeChecker
        return select(task for task in Task
                      if (task.user_id == user_id) and (task.done is None) and (task.due is None)
                      ).order_by(lambda t: t.due)[:]

    @db_session
    def complete_task(self, task_id):
        """ :returns True if completed, False if has been completed already """
        if Task[task_id].done is None:
            Task[task_id].done = datetime.utcnow()
            commit()
            return True
        return False

    @db_session
    def get_task(self, task_id):
        return Task[task_id]

    @db_session
    def remove_tasks(self, user_id, chat_id):
        # noinspection PyTypeChecker
        tasks = select(task for task in Task if task.user_id == user_id and task.chat_id == chat_id)[:]
        for task in tasks:
            task.delete()
            commit()


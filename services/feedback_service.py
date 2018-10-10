from datetime import datetime

from pony.orm import commit, db_session, select, ObjectNotFound

from data.db import Feedback
from decorators.db_use_utf8mb import db_use_utf8mb


class FeedbackService:
    @db_session
    @db_use_utf8mb
    def add(self, user_id, text):
        Feedback(user_id=user_id, text=text, created=datetime.utcnow())
        commit()

    @db_session
    @db_use_utf8mb
    def get(self, feedback_id):
        try:
            return Feedback[feedback_id]
        except ObjectNotFound:
            return None

    @db_session
    @db_use_utf8mb
    def set_resolved(self, feedback_id):
        Feedback[feedback_id].done = datetime.utcnow()
        commit()

    @db_session
    @db_use_utf8mb
    def get_all(self):
        # noinspection PyTypeChecker
        return select(feedback for feedback in Feedback)[:]

    @db_session
    @db_use_utf8mb
    def get_stats(self):
        # noinspection PyTypeChecker
        return {
            'count': select(feedback for feedback in Feedback).count(False)
        }

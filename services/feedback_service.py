from datetime import datetime

from pony.orm import commit, db_session, select, ObjectNotFound

from data.db import Feedback


class FeedbackService:
    @db_session
    def add(self, user_id, text):
        Feedback(user_id=user_id, text=text, created=datetime.utcnow())
        commit()

    @db_session
    def get(self, feedback_id):
        try:
            return Feedback[feedback_id]
        except ObjectNotFound:
            return None

    @db_session
    def set_resolved(self, feedback_id):
        Feedback[feedback_id].done = datetime.utcnow()
        commit()

    @db_session
    def get_all(self):
        # noinspection PyTypeChecker
        return select(feedback for feedback in Feedback)[:]

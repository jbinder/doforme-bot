import os
import unittest
from datetime import datetime, timedelta
from unittest import mock

from pony.orm import db_session


class TestTaskService(unittest.TestCase):

    chat_id: int

    @mock.patch.dict(os.environ, {'DFM_ENV': 'Test'})
    def setUp(self):
        from data.db import db
        from services.task_service import TaskService
        self.chat_id = 1
        self.service = TaskService()
        db.drop_all_tables(with_all_data=True)
        db.create_tables()
        self._populate_database(db)

    def test_stats_all(self):
        stats = self.service.get_stats(self.chat_id)

        created_stats = stats[0]
        expected_created_stats = self._get_expected_last_week_created_stats()
        self.assertEqual(expected_created_stats, created_stats, "Invalid created tasks stats.")

        done_stats = stats[1]
        expected_done_stats = self._get_expected_last_week_done_stats()
        self.assertEqual(expected_done_stats, done_stats, "Invalid done tasks stats.")

    def test_stats_last_week(self):
        stats = self.service.get_stats(self.chat_id, self._get_date(-7))

        created_stats = stats[0]
        expected_created_stats = self._get_expected_last_week_created_stats()
        self.assertEqual(expected_created_stats, created_stats, "Invalid created tasks stats.")

        done_stats = stats[1]
        expected_done_stats = self._get_expected_last_week_done_stats()
        self.assertEqual(expected_done_stats, done_stats, "Invalid done tasks stats.")

    def test_stats_the_week_before(self):
        stats = self.service.get_stats(self.chat_id, self._get_date(-14), self._get_date(-7))

        created_stats = stats[0]
        expected_created_stats = self._get_expected_no_tasks_stats()
        self.assertEqual(expected_created_stats, created_stats, "Invalid created tasks stats.")

        done_stats = stats[1]
        expected_done_stats = self._get_expected_no_tasks_stats()
        self.assertEqual(expected_done_stats, done_stats, "Invalid done tasks stats.")

    @staticmethod
    def _get_expected_no_tasks_stats():
        return {
            'count': 0,
            'open': {'count': 0, 'onTime': 0, 'late': 0},
            'done': {'count': 0, 'onTime': 0, 'late': 0, 'onTimePercent': 0}}

    @staticmethod
    def _get_expected_last_week_done_stats():
        return {
            'count': 1,
            'open': {'count': 0, 'onTime': 0, 'late': 0},
            'done': {'count': 1, 'onTime': 1, 'late': 0, 'onTimePercent': 100.0}}

    @staticmethod
    def _get_expected_last_week_created_stats():
        return {
            'count': 2,
            'open': {'count': 1, 'onTime': 1, 'late': 0},
            'done': {'count': 1, 'onTime': 1, 'late': 0, 'onTimePercent': 100.0}}

    @db_session
    def _populate_database(self, db):
        user1_id = 1
        user2_id = 1
        self._create_task(db, 'Task w2_done', user1_id, user2_id, self._get_date(-3), self._get_date(-5))
        self._create_task(db, 'Task w2_open', user1_id, user2_id, self._get_date(-3), None)

    @staticmethod
    def _get_date(offset_days):
        return datetime.utcnow() + timedelta(days=offset_days)

    def _create_task(self, db, title, user1_id, user2_id, created, done):
        db.Task(
            user_id=user1_id,
            chat_id=self.chat_id,
            owner_id=user2_id,
            title=title,
            created=created,
            done=done)


if __name__ == '__main__':
    unittest.main()
